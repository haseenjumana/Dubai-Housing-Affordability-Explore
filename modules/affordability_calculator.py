import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_affordability_calculator():
    """
    Display an affordability calculator to help users determine what they can afford
    """
    st.header("Housing Affordability Calculator")
    st.write("Calculate how much housing you can afford based on your income and expenses.")
    
    # Create a form for user inputs
    with st.form("affordability_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Income")
            yearly_income = st.number_input(
                "Annual Income (AED)",
                min_value=0,
                value=200000,
                step=10000,
                help="Your total annual income before taxes"
            )
            
            additional_income = st.number_input(
                "Additional Monthly Income (AED)",
                min_value=0,
                value=0,
                step=500,
                help="Any additional monthly income such as bonuses, rental income, etc."
            )
            
            st.subheader("Savings")
            down_payment = st.number_input(
                "Available Down Payment (AED)",
                min_value=0,
                value=50000,
                step=10000,
                help="Amount you have available for a down payment if purchasing"
            )
        
        with col2:
            st.subheader("Monthly Expenses")
            debt_payments = st.number_input(
                "Monthly Debt Payments (AED)",
                min_value=0,
                value=2000,
                step=500,
                help="Car loans, credit cards, personal loans, etc."
            )
            
            other_expenses = st.number_input(
                "Other Monthly Expenses (AED)",
                min_value=0,
                value=5000,
                step=500,
                help="Food, transportation, entertainment, etc."
            )
            
            st.subheader("Housing Preferences")
            preferred_areas = st.multiselect(
                "Preferred Areas",
                ["Downtown Dubai", "Dubai Marina", "Jumeirah Beach Residence", "Business Bay", 
                 "Arabian Ranches", "Dubai Silicon Oasis", "Jumeirah Village Circle", 
                 "Motor City", "Dubai Sports City", "International City"],
                default=["Dubai Marina", "Business Bay"]
            )
            
            preferred_property_type = st.selectbox(
                "Preferred Property Type",
                ["Apartment", "Villa", "Townhouse", "Any"]
            )
            
            preferred_bedrooms = st.selectbox(
                "Preferred Bedrooms",
                ["Studio", "1", "2", "3", "4+", "Any"]
            )
        
        # Calculator settings
        with st.expander("Calculator Settings"):
            rent_income_ratio = st.slider(
                "Recommended Rent to Income Ratio (%)",
                min_value=20,
                max_value=40,
                value=30,
                help="Percentage of income that should go toward housing (30% is standard)"
            )
            
            mortgage_interest = st.slider(
                "Mortgage Interest Rate (%)",
                min_value=1.0,
                max_value=10.0,
                value=4.0,
                step=0.1,
                help="Current mortgage interest rate"
            )
            
            mortgage_term = st.slider(
                "Mortgage Term (years)",
                min_value=5,
                max_value=30,
                value=25,
                step=1,
                help="Length of mortgage loan"
            )
        
        submitted = st.form_submit_button("Calculate Affordability")
    
    if submitted or "show_results" in st.session_state:
        # Set a session state variable to show results even after the form is reset
        st.session_state.show_results = True
        
        # Calculate monthly income
        monthly_income = yearly_income / 12 + additional_income
        
        # Calculate affordable monthly rent based on income ratio
        affordable_rent = monthly_income * (rent_income_ratio / 100)
        
        # Calculate affordable yearly rent
        affordable_yearly_rent = affordable_rent * 12
        
        # Calculate affordable purchase price based on mortgage parameters
        monthly_payment_capacity = affordable_rent - debt_payments
        
        # Calculate the maximum mortgage amount
        r = mortgage_interest / 100 / 12  # Monthly interest rate
        n = mortgage_term * 12  # Total number of payments
        
        # Maximum mortgage amount calculation using the present value formula
        if r > 0:
            max_mortgage = monthly_payment_capacity * ((1 - (1 + r) ** -n) / r)
        else:
            max_mortgage = monthly_payment_capacity * n
        
        # Maximum purchase price including down payment
        max_purchase_price = max_mortgage + down_payment
        
        # Display results
        st.subheader("Affordability Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Affordable Monthly Rent", f"{affordable_rent:,.0f} AED")
            st.metric("Affordable Yearly Rent", f"{affordable_yearly_rent:,.0f} AED")
        
        with col2:
            st.metric("Maximum Purchase Price", f"{max_purchase_price:,.0f} AED")
            st.metric("Maximum Mortgage Amount", f"{max_mortgage:,.0f} AED")
        
        # Show a detailed breakdown of the affordability calculation
        with st.expander("View Detailed Calculation"):
            st.write("### Monthly Income Breakdown")
            income_data = {
                "Category": ["Monthly Income", "Recommended Housing Budget", "Monthly Debt Payments", "Other Expenses", "Remaining Budget"],
                "Amount (AED)": [
                    monthly_income,
                    affordable_rent,
                    debt_payments,
                    other_expenses,
                    monthly_income - affordable_rent - debt_payments - other_expenses
                ]
            }
            
            income_df = pd.DataFrame(income_data)
            
            # Create a bar chart for the income breakdown
            fig = px.bar(
                income_df,
                x="Category",
                y="Amount (AED)",
                title="Monthly Budget Breakdown",
                color="Category",
                text_auto='.0f'
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mortgage calculation details
            st.write("### Mortgage Calculation Details")
            st.write(f"Down Payment: {down_payment:,.0f} AED")
            st.write(f"Loan Amount: {max_mortgage:,.0f} AED")
            st.write(f"Interest Rate: {mortgage_interest:.2f}%")
            st.write(f"Loan Term: {mortgage_term} years")
            st.write(f"Estimated Monthly Mortgage Payment: {monthly_payment_capacity:,.0f} AED")
        
        # Show a pie chart of expenses
        expense_data = {
            "Category": ["Housing", "Debt Payments", "Other Expenses", "Savings/Discretionary"],
            "Amount (AED)": [
                affordable_rent,
                debt_payments,
                other_expenses,
                max(0, monthly_income - affordable_rent - debt_payments - other_expenses)
            ]
        }
        
        expense_df = pd.DataFrame(expense_data)
        
        fig = px.pie(
            expense_df,
            values="Amount (AED)",
            names="Category",
            title="Recommended Monthly Expense Allocation",
            color="Category",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mortgage vs. Rent comparison
        st.subheader("Rent vs. Buy Comparison")
        
        # Calculate projected costs over time
        years = list(range(1, 11))
        
        # Assume rent increases by 5% per year
        rent_costs = [affordable_yearly_rent * ((1 + 0.05) ** i) for i in range(len(years))]
        cumulative_rent = np.cumsum(rent_costs)
        
        # Calculate mortgage principal and interest payments
        monthly_mortgage = max_mortgage * (r * (1 + r) ** n) / ((1 + r) ** n - 1) if r > 0 else max_mortgage / n
        yearly_mortgage = monthly_mortgage * 12
        mortgage_costs = [yearly_mortgage] * len(years)
        cumulative_mortgage = np.cumsum(mortgage_costs)
        
        # Add in down payment to first year of mortgage
        cumulative_mortgage = cumulative_mortgage + down_payment
        
        # Assume property value appreciates by 3% per year
        property_values = [max_purchase_price * ((1 + 0.03) ** i) for i in range(len(years))]
        
        # Calculate net cost of buying (mortgage payments - property value appreciation)
        net_buying_cost = cumulative_mortgage - np.array(property_values) + max_purchase_price
        
        # Create comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_rent,
            mode="lines+markers",
            name="Cumulative Rent Cost",
            line=dict(color="red", width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=net_buying_cost,
            mode="lines+markers",
            name="Net Cost of Buying",
            line=dict(color="green", width=2)
        ))
        
        fig.update_layout(
            title="Cumulative Cost Comparison: Renting vs. Buying",
            xaxis_title="Years",
            yaxis_title="Cost (AED)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("This comparison assumes 5% annual rent increases and 3% annual property value appreciation. Actual results may vary based on market conditions.")
        
        # Housing recommendations based on affordability
        st.subheader("Housing Recommendations")
        
        # Normally we would query a database here for actual recommendations
        # For now, we'll generate some placeholder recommendations
        
        if preferred_property_type == "Any":
            property_options = ["Apartment", "Villa", "Townhouse"]
        else:
            property_options = [preferred_property_type]
        
        if preferred_bedrooms == "Any":
            bedroom_options = ["Studio", "1", "2", "3", "4+"]
        else:
            bedroom_options = [preferred_bedrooms]
        
        st.write(f"Based on your budget of **{affordable_yearly_rent:,.0f} AED/year** for rent or **{max_purchase_price:,.0f} AED** for purchase, here are some housing options to consider:")
        
        # Different recommendations based on budget levels
        if affordable_yearly_rent < 40000:
            st.write("### Affordable Options")
            st.write("""
            With your current budget, you might consider:
            - Studios or shared accommodations in areas like International City, Dubai Silicon Oasis, or Al Qusais
            - Commuting from neighboring emirates such as Sharjah or Ajman where rental costs are lower
            - Co-living arrangements to split costs
            """)
        elif affordable_yearly_rent < 80000:
            st.write("### Mid-Range Options")
            st.write("""
            Your budget allows for:
            - Studios or 1-bedroom apartments in areas like Discovery Gardens, JVC, or Sports City
            - Potentially small 2-bedroom apartments in more affordable areas
            - Consider newer developments in emerging areas for better value
            """)
        else:
            st.write("### Premium Options")
            st.write("""
            Your budget allows for comfortable living in most areas:
            - 1-3 bedroom apartments in established communities
            - Potential villas or townhouses in certain areas
            - Access to premium amenities and locations
            """)
        
        # General advice
        st.info("""
        **Dubai Housing Tips:**
        - Negotiate your rent! Many landlords are willing to negotiate, especially for longer lease terms
        - Check the RERA Rent Calculator to ensure you're not being charged above market rates
        - Consider the total cost of living including DEWA (utilities), internet, and cooling fees
        - Factor in transportation costs - living near a Metro station can save significant commuting costs
        """)
        
        # Call to action
        st.success("Ready to start your housing search? Contact real estate agents or explore property listings on popular Dubai real estate websites.")
