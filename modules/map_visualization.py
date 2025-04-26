import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import altair as alt
from utils.constants import DUBAI_COORDINATES, NEIGHBORHOOD_INFO

def show_map_visualization(data):
    """
    Display an interactive map visualization of housing prices in Dubai
    
    Parameters:
    - data: DataFrame containing Dubai housing data
    """
    st.header("Dubai Housing Price Map")
    st.write("Explore rental prices across different neighborhoods in Dubai. Use the filters to customize your search.")
    
    # Filters in the sidebar
    st.sidebar.subheader("Map Filters")
    
    # Property type filter
    property_types = ["All"] + sorted(data["property_type"].unique().tolist())
    selected_property_type = st.sidebar.selectbox("Property Type", property_types)
    
    # Number of bedrooms filter
    bedroom_options = ["All", "Studio", "1", "2", "3", "4+"]
    selected_bedrooms = st.sidebar.selectbox("Bedrooms", bedroom_options)
    
    # Price range filter
    max_price = int(data["price_yearly_aed"].max())
    price_range = st.sidebar.slider(
        "Yearly Rent Range (AED)",
        min_value=0,
        max_value=max_price,
        value=(0, int(max_price * 0.6)),
        step=5000
    )
    
    # Filter data based on selections
    filtered_data = data.copy()
    
    if selected_property_type != "All":
        filtered_data = filtered_data[filtered_data["property_type"] == selected_property_type]
    
    if selected_bedrooms != "All":
        if selected_bedrooms == "Studio":
            filtered_data = filtered_data[filtered_data["bedrooms"] == 0]
        elif selected_bedrooms == "4+":
            filtered_data = filtered_data[filtered_data["bedrooms"] >= 4]
        else:
            filtered_data = filtered_data[filtered_data["bedrooms"] == int(selected_bedrooms)]
    
    filtered_data = filtered_data[
        (filtered_data["price_yearly_aed"] >= price_range[0]) &
        (filtered_data["price_yearly_aed"] <= price_range[1])
    ]
    
    # Create two columns for the map and stats
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a map centered on Dubai
        dubai_map = folium.Map(
            location=DUBAI_COORDINATES["center"],
            zoom_start=11,
            tiles="OpenStreetMap"
        )
        
        # Group data by neighborhood for circle markers
        neighborhood_data = filtered_data.groupby("neighborhood").agg({
            "price_yearly_aed": ["mean", "count"],
            "lat": "mean",
            "lng": "mean"
        })
        
        neighborhood_data.columns = ["avg_price", "property_count", "lat", "lng"]
        neighborhood_data = neighborhood_data.reset_index()
        
        # Add circle markers for each neighborhood
        for _, row in neighborhood_data.iterrows():
            if pd.notna(row["lat"]) and pd.notna(row["lng"]):
                # Scale circle size by number of properties
                radius = min(10 + (row["property_count"] * 0.5), 30)
                
                # Color based on price (darker = more expensive)
                max_avg_price = neighborhood_data["avg_price"].max()
                price_ratio = row["avg_price"] / max_avg_price
                color = f"#{int(255 * (1 - price_ratio)):02x}{int(180 * (1 - price_ratio)):02x}00"
                
                # Create popup with neighborhood info
                popup_text = f"""
                <b>{row['neighborhood']}</b><br>
                Average Price: AED {int(row['avg_price']):,} / year<br>
                Available Properties: {row['property_count']}<br>
                """
                
                folium.CircleMarker(
                    location=[row["lat"], row["lng"]],
                    radius=radius,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(dubai_map)
        
        # Display the map
        folium_static(dubai_map)
        
        # Additional info about the map
        st.info("Click on any circle to see detailed information about that neighborhood. Larger circles indicate more available properties. Darker colors indicate higher prices.")
    
    with col2:
        # Show stats about the filtered data
        st.subheader("Housing Statistics")
        
        if len(filtered_data) > 0:
            avg_price = int(filtered_data["price_yearly_aed"].mean())
            median_price = int(filtered_data["price_yearly_aed"].median())
            count = len(filtered_data)
            
            st.metric("Available Properties", f"{count:,}")
            st.metric("Average Yearly Rent", f"AED {avg_price:,}")
            st.metric("Median Yearly Rent", f"AED {median_price:,}")
            
            # Create a chart showing price distribution
            price_chart = alt.Chart(filtered_data).mark_bar().encode(
                x=alt.X('price_yearly_aed:Q', bin=True, title='Yearly Rent (AED)'),
                y=alt.Y('count()', title='Number of Properties')
            ).properties(
                title='Price Distribution',
                height=200
            )
            
            st.altair_chart(price_chart, use_container_width=True)
            
            # Show top 5 most affordable neighborhoods
            st.subheader("Most Affordable Neighborhoods")
            
            if "neighborhood" in filtered_data.columns:
                affordable_neighborhoods = (
                    filtered_data.groupby("neighborhood")
                    .agg({"price_yearly_aed": "mean", "property_type": "count"})
                    .rename(columns={"property_type": "count"})
                    .sort_values("price_yearly_aed")
                    .reset_index()
                    .head(5)
                )
                
                for i, row in affordable_neighborhoods.iterrows():
                    st.write(f"{i+1}. **{row['neighborhood']}** - AED {int(row['price_yearly_aed']):,}/year")
        else:
            st.warning("No properties match your selected filters. Please adjust your criteria.")
    
    # Display some featured affordable properties
    if len(filtered_data) > 0:
        st.subheader("Featured Affordable Properties")
        
        # Sort by price and get the most affordable options
        affordable_properties = filtered_data.sort_values("price_yearly_aed").head(6)
        
        # Create a 3x2 grid for property cards
        cols = st.columns(3)
        
        for i, (_, property_row) in enumerate(affordable_properties.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <h4>{property_row['property_type']} in {property_row['neighborhood']}</h4>
                        <p>
                            {'Studio' if property_row['bedrooms'] == 0 else f"{int(property_row['bedrooms'])} BR"} 
                            | {int(property_row['size_sqft'])} sqft
                        </p>
                        <p style="font-weight: bold; color: #E6B800;">AED {int(property_row['price_yearly_aed']):,}/year</p>
                        <p>AED {int(property_row['price_monthly_aed']):,}/month</p>
                    </div>
                """, unsafe_allow_html=True)
