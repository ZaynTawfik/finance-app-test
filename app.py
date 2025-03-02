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
    page = st.sidebar.radio("Menu", ["Profile Setup", "Financial Goals", "Recommendations","Settings"])

    # Profile Setup Page
    if page == "Profile Setup":
        st.header("Personal Financial Profile")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.profile['age'] = st.number_input("Current Age", min_value=18, max_value=100, value=30)
                st.session_state.profile['income'] = st.number_input("Monthly Income ($)", min_value=0, value=5000)
                st.session_state.profile['monthly_expense'] = st.number_input("Monthly Expenses ($)", min_value=0, value=10000)
                st.session_state.profile['roi_pct'] = st.number_input("ROI p.a.", min_value=0, value=100)
                
            with col2:
                st.session_state.profile['monthly_investments'] = st.number_input("Monthly Investments ($)", min_value=0, value=1000)
                st.session_state.profile['loans'] = st.number_input("Monthly Loan EMIs ($)", min_value=0, value=500)
                st.session_state.profile['current_portfolio'] = st.number_input("Portfolio ($)", min_value=0, value=3000)
            
            if st.form_submit_button("Save Profile"):
                st.success("Profile updated successfully!")

    # Financial Goals Page
    elif page == "Financial Goals":
        st.header("Financial Goals Planning")
        with st.expander("Add New Goal"):
            with st.form("goal_form"):
                goal_name = st.text_input("Goal Name")
                target_age = st.number_input("Target Age", min_value=st.session_state.profile['age'], max_value=100, value=st.session_state.profile['age'])
                target_amount = st.number_input("Target Amount ($)", min_value=0, value=50000)
                
                if st.form_submit_button("Add Goal"):
                    st.session_state.goals.append({
                        'name': goal_name,
                        'age': target_age,
                        'amount': target_amount
                    })
                    st.success("Goal added!")
        
        st.subheader("Current Goals")
        goals_df = pd.DataFrame(st.session_state.goals)
        if not goals_df.empty:
            st.dataframe(goals_df)
            if st.button("Recalculate Retirement Plan"):
                first_goal = st.session_state.goals[0]
                financial_milestone = (first_goal['amount'], first_goal['age'])
                retirement_age, retirement_money = calculate_retirement(
                    st.session_state.profile['age'],
                    st.session_state.profile['income'],
                    3000,
                    2000,
                    100000,
                    st.session_state.profile['roi_pct'],
                    financial_milestone,
                    st.session_state.settings['life_expectancy'],
                    st.session_state.settings['inflation'],
                    st.session_state.settings['emergency_funds'],
                    st.session_state.settings['investment_increase'])
                st.session_state.profile['retirement_age'] = retirement_age
                st.success(f"Updated Projected Retirement Age: {retirement_age} with {retirement_money}")
        else:
            st.info("No goals added yet")
'''
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
'''
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
            inflation = st.number_input("Inflation Rate (% p.a.)", 
                                      min_value=0.0, max_value=20.0, 
                                      value=st.session_state.settings['inflation'])
            life_expectancy = st.number_input("Life Expectancy (years)", 
                                            min_value=60, max_value=120, 
                                            value=st.session_state.settings['life_expectancy'])
            emergency_funds = st.number_input("Emergency Funds (months)", 
                                             min_value=3, max_value=60, 
                                             value=st.session_state.settings['emergency_funds'])
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

def calculate_retirement(
    age: int,
    monthly_income: float,
    monthly_expense: float,
    monthly_investments: float,
    current_portfolio: float,
    roi_pct: float,
    financial_milestone_goal: tuple,
    life_expectancy: int,
    inflation_pct: float,
    emergency_funds_months: float,
    investment_increase_pct: float,
) -> tuple:
    # Convert percentages to decimal
    roi = roi_pct / 100.0
    inflation = inflation_pct / 100.0
    investment_increase = investment_increase_pct / 100.0

    current_age = age
    portfolio = current_portfolio
    monthly_invest = monthly_investments  # Track monthly investments, increasing annually

    milestone_amount, milestone_age = financial_milestone_goal

    for current_age in range(age, life_expectancy + 1):
        # Check if this is the milestone year and apply deduction
        if current_age == milestone_age:
            portfolio -= milestone_amount
            portfolio = max(portfolio, 0)  # Ensure portfolio doesn't go negative

        # Calculate required portfolio to retire at current_age
        years_until_retirement = current_age - age
        annual_expense_at_retirement = 12 * monthly_expense * (1 + inflation) ** years_until_retirement
        retirement_years = life_expectancy - current_age

        if retirement_years <= 0:
            required = 0.0
        else:
            if roi == inflation:
                required = annual_expense_at_retirement * retirement_years
            else:
                g = (1 + inflation) / (1 + roi)
                required = annual_expense_at_retirement * (1 - g ** retirement_years) / (1 - g)

        # Check if portfolio meets the required amount to retire
        if portfolio >= required:
            return (current_age, portfolio)

        # If not retiring this year, add investments and grow portfolio
        annual_investment = monthly_invest * 12
        portfolio += annual_investment
        portfolio *= (1 + roi)
        monthly_invest *= (1 + investment_increase)  # Increase investments for next year

    return (life_expectancy, portfolio)

if __name__ == "__main__":
    main()
