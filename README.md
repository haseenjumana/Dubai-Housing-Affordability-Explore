# Dubai Housing Affordability Explorer

A comprehensive data visualization tool to help Dubai residents find affordable housing options through interactive maps, trend analysis, and personalized affordability calculations.

## Features

- **Interactive Housing Map**: Visualize rental properties across Dubai neighborhoods with price-based filtering
- **Rental Price Trends**: Analyze how rental prices have changed over time in different areas
- **Neighborhood Comparison**: Compare multiple neighborhoods based on affordability, amenities, and lifestyle factors
- **Affordability Calculator**: Calculate what you can afford based on your income and expenses
- **Housing Resources**: Access information about tenant rights and affordable housing initiatives

## Installation

1. Clone this repository:
```bash
git clone https://github.com/haseenjumana/dubai-housing-explorer.git
cd dubai-housing-explorer

2.Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3.Install required packages:

pip install -r requirements.txt

4.Run the application:
streamlit run app.py

structure of project
dubai-housing-explorer/
│
├── .streamlit/          # Streamlit configuration
├── modules/             # Feature modules
├── utils/               # Utility functions and constants
├── app.py               # Main application file
└── requirements.txt     # Dependencies

Required Packages
streamlit==1.32.0
pandas==2.1.1
numpy==1.26.0
folium==0.14.0
streamlit-folium==0.15.0
plotly==5.18.0
altair==5.2.0

Deployment
The application can be deployed on Streamlit Cloud or any hosting platform that supports Python applications.

Data Sources
This application uses data sourced from official Dubai property listings and records.
