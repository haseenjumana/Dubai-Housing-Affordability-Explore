import pandas as pd
import numpy as np
import streamlit as st
import os
from datetime import datetime, timedelta
import time
import random
from utils.constants import DUBAI_COORDINATES, NEIGHBORHOOD_INFO

@st.cache_data(ttl=3600)
def load_dubai_housing_data():
    """
    Load Dubai housing data from a data source.
    
    In a real application, this would fetch data from a database, API, or CSV file.
    Since we don't have access to real data in this example, this function creates 
    synthetic data based on typical Dubai rental patterns.
    
    Returns:
        DataFrame: A pandas DataFrame containing housing data
    """
    try:
        # Simulate a small delay to mimic data loading
        time.sleep(1)
        
        # In a real application, you would load data from a real source:
        # Example:
        # data = pd.read_csv('path/to/dubai_housing_data.csv')
        # or
        # data = pd.read_json('https://api.example.com/dubai-housing-data')
        
        # Since we don't have real data, we'll create a structured dataset
        # that represents the Dubai housing market
        
        # This is a list of representative Dubai neighborhoods
        neighborhoods = list(NEIGHBORHOOD_INFO.keys())
        
        # Create areas based on neighborhoods (each area contains multiple neighborhoods)
        areas = {
            "Downtown": ["Downtown Dubai", "Business Bay", "DIFC"],
            "Marina Area": ["Dubai Marina", "JBR", "JLT"],
            "Palm Jumeirah": ["Palm Jumeirah"],
            "New Dubai": ["Dubai Hills Estate", "Arabian Ranches", "Emirates Hills"],
            "Academic City": ["Dubai Silicon Oasis", "Academic City", "International City"],
            "Sports City": ["Sports City", "Motor City", "JVC"],
            "Old Dubai": ["Deira", "Bur Dubai", "Al Karama"]
        }
        
        # Reverse map from neighborhood to area
        neighborhood_to_area = {}
        for area, nbs in areas.items():
            for nb in nbs:
                neighborhood_to_area[nb] = area
        
        # Property types
        property_types = ["Apartment", "Villa", "Townhouse", "Penthouse", "Studio"]
        
        # Number of records to generate
        num_records = 1000
        
        # Current date
        today = datetime.now()
        
        # Create lists for each column
        data_dict = {
            "id": list(range(1, num_records + 1)),
            "neighborhood": [],
            "area": [],
            "property_type": [],
            "bedrooms": [],
            "bathrooms": [],
            "size_sqft": [],
            "price_yearly_aed": [],
            "price_monthly_aed": [],
            "date_posted": [],
            "lat": [],
            "lng": []
        }
        
        for _ in range(num_records):
            # Select a random neighborhood
            neighborhood = random.choice(neighborhoods)
            
            # Get the area for the neighborhood
            area = neighborhood_to_area.get(neighborhood, "Other")
            
            # Select a property type with weighted probability
            # Apartments are more common
            prop_type_weights = [0.7, 0.1, 0.1, 0.05, 0.05]
            property_type = random.choices(property_types, weights=prop_type_weights)[0]
            
            # Assign bedrooms based on property type
            if property_type == "Studio":
                bedrooms = 0
            elif property_type == "Apartment":
                bedrooms = random.choices([1, 2, 3, 4], weights=[0.4, 0.4, 0.15, 0.05])[0]
            elif property_type == "Penthouse":
                bedrooms = random.choices([2, 3, 4, 5], weights=[0.1, 0.3, 0.4, 0.2])[0]
            else:  # Villa or Townhouse
                bedrooms = random.choices([2, 3, 4, 5, 6], weights=[0.05, 0.3, 0.4, 0.2, 0.05])[0]
            
            # Bathrooms are generally related to bedrooms
            bathrooms = max(1, min(bedrooms, random.choices(
                [bedrooms - 1, bedrooms, bedrooms + 1], 
                weights=[0.3, 0.6, 0.1]
            )[0]))
            
            # Size depends on property type and bedrooms
            if property_type == "Studio":
                size_sqft = random.randint(300, 600)
            elif property_type == "Apartment":
                base_size = 600
                size_sqft = base_size + (bedrooms * random.randint(200, 400))
            elif property_type == "Penthouse":
                base_size = 1500
                size_sqft = base_size + (bedrooms * random.randint(400, 700))
            else:  # Villa or Townhouse
                base_size = 1200
                size_sqft = base_size + (bedrooms * random.randint(500, 800))
            
            # Price depends on area, property type, size, and bedrooms
            # Base price per sqft varies by area
            area_price_factors = {
                "Downtown": 1.5,
                "Marina Area": 1.3,
                "Palm Jumeirah": 1.8,
                "New Dubai": 1.1,
                "Academic City": 0.7,
                "Sports City": 0.8,
                "Old Dubai": 0.9
            }
            
            # Property type price factors
            property_type_factors = {
                "Apartment": 1.0,
                "Villa": 1.3,
                "Townhouse": 1.2,
                "Penthouse": 1.5,
                "Studio": 0.9
            }
            
            # Base price per sqft in AED (yearly)
            base_price_per_sqft = 90  # AED per sqft per year
            
            # Calculate yearly price
            price_factor = area_price_factors.get(area, 1.0) * property_type_factors.get(property_type, 1.0)
            price_per_sqft = base_price_per_sqft * price_factor
            
            # Add some randomness
            price_per_sqft = price_per_sqft * random.uniform(0.9, 1.1)
            
            # Calculate yearly price
            price_yearly_aed = int(size_sqft * price_per_sqft)
            
            # Monthly price is yearly / 12 (rounded to nearest 100)
            price_monthly_aed = int(round(price_yearly_aed / 12, -2))
            
            # Random date posted within the last 180 days
            date_posted = today - timedelta(days=random.randint(1, 180))
            
            # Get coordinates for the neighborhood with some randomness
            if neighborhood in NEIGHBORHOOD_INFO and "coordinates" in NEIGHBORHOOD_INFO[neighborhood]:
                base_lat = NEIGHBORHOOD_INFO[neighborhood]["coordinates"][0]
                base_lng = NEIGHBORHOOD_INFO[neighborhood]["coordinates"][1]
            else:
                # Use Dubai center coordinates as fallback
                base_lat = DUBAI_COORDINATES["center"][0]
                base_lng = DUBAI_COORDINATES["center"][1]
            
            # Add small random variations to coordinates
            lat = base_lat + random.uniform(-0.01, 0.01)
            lng = base_lng + random.uniform(-0.01, 0.01)
            
            # Append to the data dictionary
            data_dict["neighborhood"].append(neighborhood)
            data_dict["area"].append(area)
            data_dict["property_type"].append(property_type)
            data_dict["bedrooms"].append(bedrooms)
            data_dict["bathrooms"].append(bathrooms)
            data_dict["size_sqft"].append(size_sqft)
            data_dict["price_yearly_aed"].append(price_yearly_aed)
            data_dict["price_monthly_aed"].append(price_monthly_aed)
            data_dict["date_posted"].append(date_posted)
            data_dict["lat"].append(lat)
            data_dict["lng"].append(lng)
        
        # Create the DataFrame
        df = pd.DataFrame(data_dict)
        
        # Add derived columns
        df["price_per_sqft"] = df["price_yearly_aed"] / df["size_sqft"]
        
        # Return the DataFrame
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None
