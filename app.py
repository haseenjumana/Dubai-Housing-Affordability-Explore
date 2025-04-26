import streamlit as st
import pandas as pd
import os

from modules.map_visualization import show_map_visualization
from modules.trend_analysis import show_trend_analysis
from modules.comparison_tool import show_comparison_tool
from modules.affordability_calculator import show_affordability_calculator
from utils.data_loader import load_dubai_housing_data

# Page Configuration must be first Streamlit command
st.set_page_config(
    page_title="Dubai Housing Affordability",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit menu and footer (after page config)
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# App title and description
st.title("Dubai Housing Affordability Explorer")
st.markdown("""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px;'>
    <h3>Find affordable housing options in Dubai</h3>
    <p>Explore rental prices, analyze trends, compare neighborhoods, and calculate what you can afford.</p>
    </div>
""", unsafe_allow_html=True)

# Load data
try:
    with st.spinner("Loading Dubai housing data..."):
        data = load_dubai_housing_data()
        
    if data is None or data.empty:
        st.error("Unable to load housing data. Please try again later.")
        st.stop()
        
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a feature:",
    ["Interactive Map", "Rental Trends", "Neighborhood Comparison", "Affordability Calculator", "Housing Resources"]
)

# About section in sidebar
with st.sidebar.expander("About this app"):
    st.write("""
    The Dubai Housing Affordability Explorer helps residents find affordable 
    housing options through interactive visualizations and tools. 
    Data is sourced from official Dubai property listings and records.
    """)

# Contact info in sidebar
with st.sidebar.expander("Contact Information"):
    st.write("""
    - **Housing Authority Dubai:** +971-4-XXX-XXXX
    - **Rental Dispute Center:** +971-4-XXX-XXXX
    - **RERA (Real Estate Regulatory Agency):** +971-4-XXX-XXXX
    """)

# Display the selected page
if page == "Interactive Map":
    show_map_visualization(data)
    
elif page == "Rental Trends":
    show_trend_analysis(data)
    
elif page == "Neighborhood Comparison":
    show_comparison_tool(data)
    
elif page == "Affordability Calculator":
    show_affordability_calculator()
    
elif page == "Housing Resources":
    st.header("Housing Resources")
    
    st.subheader("Tenant Rights in Dubai")
    st.write("""
    ### Rental Regulations
    - Landlords can only increase rent according to RERA's rent calculator
    - Eviction requires 12 months' notice via notary public or registered mail
    - Security deposit is typically 5% of annual rent, refundable at end of tenancy
    
   ### Useful Links
- [Dubai Land Department](https://dubailand.gov.ae/en/)
- [RERA Rent Calculator](https://www.calculatoruae.com/calculators/rent-index)
- [Rental Dispute Center](https://rdc.gov.ae/en/#/)

 """)
    
    st.subheader("Affordable Housing Initiatives")
    st.write("""
    ### Government Programs
    - Dubai's Affordable Housing Policy
    - Mohammed Bin Rashid Housing Establishment
    - Sheikh Zayed Housing Programme
    
    ### Private Sector Initiatives
    - Middle-income housing developers
    - Rent-to-own schemes
    - Co-living arrangements
    """)
    
# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <p>© 2023 Dubai Housing Affordability Explorer | All data sourced from official records</p>
    </div>
""", unsafe_allow_html=True)