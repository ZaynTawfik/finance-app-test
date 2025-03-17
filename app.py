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

#from crewai_tools import FileReadTool
#csv_tool = FileReadTool(file_path='./transactions.csv')

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
    if 'investments' not in st.session_state:
        st.session_state.investments = {}
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'inflation': 6.0,
            'life_expectancy': 90,
            'emergency_funds': 24,
            'investment_increase': 10.0
        }

    st.sidebar.image("logo.png",caption="Dream Big. We'll handle the math.")
    st.sidebar.divider()
    
    page = st.sidebar.radio("Menu", ["Profile Setup", "Financial Goals", "Recommendations","Settings"],key='menu_radio')
    
    # About section in sidebar with styling
    with st.sidebar:
        # Create a container for better spacing control
        about_container = st.container()
    
        with about_container:
            # Title with custom styling
            st.markdown("""
            <style>
                .about-title {
                    font-size: 18px !important;
                    font-weight: 600 !important;
                    margin-bottom: 8px !important;
                }
                .about-text {
                    font-size: 14px !important;
                    line-height: 1.4 !important;
                    color: #666;
                }
            </style>
            """, unsafe_allow_html=True)
        
            # About section content
            st.markdown('<div class="about-title">About Coyn</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="about-text">'
                'Your AI-Powered Personal Financial Advisor. Automatically Analyze Financial Health, '
                'Plan Retirement, and Optimize Money Decisions with Precision. Get Tailored Reports '
                'and Actionable Strategies to Secure Your Future.'
                '</div>', 
                unsafe_allow_html=True
            )
    
    st.sidebar.divider()
    #sidebar profile
    with st.sidebar:
        # Create two columns
        col1, col2 = st.columns([1, 3])
    
        # Add profile icon to first column (using emoji or image)
        with col1:
        
            # Profile Icon
            st.image("https://img.icons8.com/?size=100&id=20751&format=png&color=000000", width=80)
    
        # Add profile name to second column
        with col2:
            st.markdown("""
            <style>
                .profile-name {
                    font-size: 1.0rem;
                    font-weight: bold;
                }
            </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="profile-name">Thoufeek Hussain</div>', unsafe_allow_html=True)
    
    
    
    # Profile Setup Page
    if page == "Profile Setup":
        st.header("Profile")
        COUNTRIES = [
        "India",
        "United States (USA)",
        "United Kingdom (UK)",
        "United Arab Emirates (UAE)",
        "Singapore"
        ]
        COUNTRY_CURRENCY = {
        "India": "INR",
        "United States (USA)": "USD",
        "United Kingdom (UK)": "GBP",
        "United Arab Emirates (UAE)": "AED",
        "Singapore": "SGD"
        }
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.profile['age'] = st.number_input("Current Age", min_value=18, max_value=100, value=25)
                st.session_state.profile['income'] = st.number_input("Avg. Monthly Income", min_value=0, value=25000)
                st.session_state.profile['monthly_investments'] = st.number_input("Avg. Monthly Investments", min_value=0, value=5000)
                
            with col2:
                st.session_state.profile['country'] = st.selectbox("Country", options=COUNTRIES, index=0)
                st.session_state.profile['monthly_expense'] = st.number_input("Avg. Monthly Expenses", min_value=0, value=13000)
                st.session_state.profile['loans'] = st.number_input("Active Monthly Loans/EMIs", min_value=0, value=0)

            st.write("Current Investment Portfolio")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.session_state.investments['Equity'] = st.number_input("Equity", min_value=0, value=125000)
                st.session_state.investments['Crypto'] = st.number_input("Crypto", min_value=0, value=10000)
                st.session_state.investments['commodity'] = st.number_input("Commodity", min_value=0, value=15000)
            with col4:
                st.session_state.investments['Bonds'] = st.number_input("Bonds", min_value=0, value=15000)
                st.session_state.investments['real_estate'] = st.number_input("Real Estate", min_value=0, value=100000)
                st.session_state.investments['roi_pct'] = st.number_input("Est. Avg. Retunrs (%)p.a.", min_value=0, value=10)
            if st.form_submit_button("Save Profile"):
                st.success("Profile updated successfully!")
            
            st.session_state.investments['current_portfolio'] = st.session_state.investments['Bonds'] + st.session_state.investments['Equity'] + st.session_state.investments['Bonds'] + st.session_state.investments['real_estate'] + st.session_state.investments['Crypto'] + st.session_state.investments['commodity'] 
            st.session_state.profile['currency'] = COUNTRY_CURRENCY.get(st.session_state.profile['country'], 'INR')
            col5, col6, col7 = st.columns(3)
            with col5:
                st.write("Current Portfolio:", st.session_state.investments['current_portfolio'] )  
            with col6:
                st.write("Monthly Savings:", st.session_state.profile['income']-st.session_state.profile['monthly_expense']-st.session_state.profile['loans'])
            with col7:
                st.write("Currency:", st.session_state.profile['currency'] )

    # Financial Goals Page
    elif page == "Financial Goals":
        st.header("Financial Goals Planning")
        st.text("")
        #st.markdown("---")
        with st.expander("Add New Goal"):
            with st.form("goal_form"):
                goal_name = st.text_input("Goal Name")
                target_age = st.number_input("Target Age", min_value=18, max_value=100, value=28)
                target_amount = st.number_input("Target Amount", min_value=0, value=0)
                
                if st.form_submit_button("Add Goal",type="tertiary"):
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
            st.text("")
            st.text("")
            if st.button("Calculate Retirement"):
                first_goal = st.session_state.goals[0]
                financial_milestone = (first_goal['amount'], first_goal['age'])
                retirement_age, retirement_money = calculate_retirement(
                    st.session_state.profile['age'],
                    st.session_state.profile['income'],
                    st.session_state.profile['monthly_expense'],
                    st.session_state.profile['monthly_investments'],
                    st.session_state.investments['current_portfolio'],
                    st.session_state.investments['roi_pct'],
                    financial_milestone,
                    st.session_state.settings['life_expectancy'],
                    st.session_state.settings['inflation'],
                    st.session_state.settings['emergency_funds'],
                    st.session_state.settings['investment_increase'])
                st.session_state.profile['retirement_age'] = retirement_age
                st.session_state.profile['retirement_money'] = retirement_money
                st.success(f"Current Projected Retirement is at age {retirement_age} with {st.session_state.profile['currency']} {retirement_money:,.2f}")
        else:
            st.info("No goals added yet")
            
    # Recommendations Page
    elif page == "Recommendations":
        st.header("Your Personalized Action Plan")
        st.markdown("---")
        if 'retirement_age' in st.session_state.profile:
            st.caption(f"Your current projected retirement is at age {st.session_state.profile['retirement_age']} with {st.session_state.profile['currency']} {st.session_state.profile['retirement_money']:,.2f}")
            st.text(st.session_state.profile['retirement_age'])
            st.caption(f"with")
            st.text(st.session_state.profile['retirement_money']:,.2f)
        st.text("")
        st.text("")
        st.text("")
        if st.session_state.profile:
            if st.button("Get Plan & Recommendations", type="primary"):
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
                  agent=wealth_manager,
                  context=[analyze_finances]
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
                    'settings' : st.session_state.settings,
                    'retirement_age' : st.session_state.profile['retirement_age'],
                    'retirement_money' : st.session_state.profile['retirement_money'],
                    'country': st.session_state.profile['country'],
                })
                st.subheader("Comprehensive Financial Plan")
                st.markdown(final_report.raw)
    # Settings Page
    elif page == "Settings":
        st.header("Financial Assumptions Settings")
        st.markdown("---")
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
