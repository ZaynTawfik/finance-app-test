# app.py (Main Application)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import pandas as pd
from crewai import Crew
from crewai import Agent, Task, Crew
from helper import load_env
import os
import yaml
# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

from crewai_tools import FileReadTool
csv_tool = FileReadTool(file_path='./transactions.csv')

# Load environment variables
load_env()

# Set OpenAI model (Update with your model choice)
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
agents_config = load_yaml('config/agents.yaml')
tasks_config = load_yaml('config/tasks.yaml')
rec_agents_config = load_yaml('config/recommend_agents.yaml')
rec_tasks_config = load_yaml('config/recommend_tasks.yaml')

def main():
    st.set_page_config(page_title="AI Financial Advisor", layout="wide")
    
    # Initialize session state
    if 'goals' not in st.session_state:
        st.session_state.goals = []
    if 'profile' not in st.session_state:
        st.session_state.profile = {}
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'inflation': 6.0,
            'life_expectancy': 90,
            'emergency_funds': 24,
            'investment_increase': 10.0
        }
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Profile Setup", "Financial Goals", "Transactions Analysis", "Recommendations"])

    # Profile Setup Page
    if page == "Profile Setup":
        st.header("Personal Financial Profile")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.profile['age'] = st.number_input("Current Age", min_value=18, max_value=100, value=30)
                st.session_state.profile['income'] = st.number_input("Monthly Income ($)", min_value=0, value=5000)
                st.session_state.profile['savings'] = st.number_input("Current Savings ($)", min_value=0, value=10000)
                
            with col2:
                st.session_state.profile['investments'] = st.number_input("Monthly Investments ($)", min_value=0, value=1000)
                st.session_state.profile['loans'] = st.number_input("Monthly Loan EMIs ($)", min_value=0, value=500)
                st.session_state.profile['expenses'] = st.number_input("Monthly Expenses ($)", min_value=0, value=3000)
            
            if st.form_submit_button("Save Profile"):
                st.success("Profile updated successfully!")

    # Financial Goals Page
    elif page == "Financial Goals":
        st.header("Financial Goals Planning")
        with st.expander("Add New Goal"):
            with st.form("goal_form"):
                goal_name = st.text_input("Goal Name")
                target_year = st.number_input("Target Year", min_value=2023, max_value=2100, value=2030)
                target_amount = st.number_input("Target Amount ($)", min_value=0, value=50000)
                
                if st.form_submit_button("Add Goal"):
                    st.session_state.goals.append({
                        'name': goal_name,
                        'year': target_year,
                        'amount': target_amount
                    })
                    st.success("Goal added!")
        
        st.subheader("Current Goals")
        goals_df = pd.DataFrame(st.session_state.goals)
        if not goals_df.empty:
            st.dataframe(goals_df)
            if st.button("Recalculate Retirement Plan"):
                retirement_age = calculate_retirement(st.session_state.profile, st.session_state.goals)
                st.session_state.profile['retirement_age'] = retirement_age
                st.success(f"Updated Projected Retirement Age: {retirement_age}")
        else:
            st.info("No goals added yet")

    # Transactions Analysis Page
    elif page == "Transactions Analysis":
        st.header("Transactions Analysis")
        csv_tool = FileReadTool(file_path='./transactions.csv')
        #uploaded_file = st.file_uploader("Upload Transactions CSV", type=["csv"])
        
        if csv_tool:
            #transactions = pd.read_csv(uploaded_file)
            #st.session_state.transactions = transactions
            
            financial_analysis_agent = Agent(config=agents_config['financial_analysis_agent'],tools=[csv_tool])
            budget_planning_agent = Agent(config=agents_config['budget_planning_agent'],tools=[csv_tool])
            financial_viz_agent = Agent(config=agents_config['financial_viz_agent'],allow_code_execution=False)

            # Create tasks
            expense_analysis = Task(
              config=tasks_config['expense_analysis'],
              agent=financial_analysis_agent
            )

            budget_management = Task(
              config=tasks_config['budget_management'],
              agent=budget_planning_agent
            )

            financial_visualization = Task(
              config=tasks_config['financial_visualization'],
              agent=financial_viz_agent
            )

            final_report_assembly = Task(
              config=tasks_config['final_report_assembly'],
              agent=budget_planning_agent,
              context=[expense_analysis, budget_management, financial_visualization]
            )

            #Create crew
            finance_crew = Crew(
              agents=[
                financial_analysis_agent,
                budget_planning_agent,
                financial_viz_agent
              ],
              tasks=[
                expense_analysis,
                budget_management,
                financial_visualization,
                final_report_assembly
              ],
              verbose=True
            )

            result = finance_crew.kickoff()
            st.session_state.analysis_result = result
            
            st.subheader("Spending Analysis")
            st.write(result.raw)

    # Recommendations Page
    elif page == "Recommendations":
        st.header("Personalized Recommendations")
        
        if 'retirement_age' in st.session_state.profile:
            st.subheader(f"Projected Retirement Age: {st.session_state.profile['retirement_age']}")
        
        if st.session_state.profile:
            #agents
            financial_analyst = Agent(config=rec_agents_config['financial_analyst'])
            wealth_manager = Agent(config=rec_agents_config['wealth_manager'])
            report_generator = Agent(config=rec_agents_config['report_generator'])
            
            #tasks
            analyze_finances = Task(
              config=rec_tasks_config['analyze_finances'],
              agent=financial_analyst
            )

            create_recommendations = Task(
              config=rec_tasks_config['create_recommendations'],
              agent=wealth_manager
            )

            generate_report = Task(
              config=rec_tasks_config['generate_report'],
              agent=report_generator,
              context=[analyze_finances, create_recommendations]
            )            
            # Generate final report
            recommend_crew = Crew(
                agents=[financial_analyst, wealth_manager, report_generator],
                tasks=[analyze_finances, create_recommendations, generate_report],
                verbose=True
            )
            
            final_report = recommend_crew.kickoff(inputs={
                'profile': st.session_state.profile,
                'goals': st.session_state.goals,
            })
            st.write(st.session_state.profile)
            st.write(st.session_state.goals)
            st.subheader("Comprehensive Financial Plan")
            st.markdown(final_report.raw)
    # Settings Page
    elif page == "Settings":
        st.header("Financial Assumptions Settings")
        with st.form("settings_form"):
            st.subheader("Economic Assumptions")
            inflation = st.number_input("Inflation Rate (% p.a.)", 
                                      min_value=0.0, max_value=20.0, 
                                      value=st.session_state.settings['inflation'])
            
            st.subheader("Personal Assumptions")
            life_expectancy = st.number_input("Life Expectancy (years)", 
                                            min_value=60, max_value=120, 
                                            value=st.session_state.settings['life_expectancy'])
            emergency_funds = st.number_input("Emergency Funds (months)", 
                                             min_value=3, max_value=60, 
                                             value=st.session_state.settings['emergency_funds'])
            
            st.subheader("Investment Growth")
            investment_increase = st.number_input("Annual Increase in Investments (%)", 
                                                 min_value=0.0, max_value=50.0, 
                                                 value=st.session_state.settings['investment_increase'])
            
            if st.form_submit_button("Save Settings"):
                st.session_state.settings = {
                    'inflation': inflation,
                    'life_expectancy': life_expectancy,
                    'emergency_funds': emergency_funds,
                    'investment_increase': investment_increase
                }
                st.success("Settings updated successfully!")

def calculate_retirement(profile, goals):
    # Simplified retirement calculation
    current_age = profile['age']
    annual_savings = (profile['income'] - profile['expenses'] - profile['loans']) * 12
    total_goals = sum(goal['amount'] for goal in goals)
    
    # Basic compound interest calculation
    years_to_retire = (total_goals - profile['savings']) / annual_savings
    return min(current_age + int(years_to_retire), 70)

if __name__ == "__main__":
    main()
