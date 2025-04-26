import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import NEIGHBORHOOD_INFO

def show_comparison_tool(data):
    """
    Display a comparison tool for different neighborhoods in Dubai
    
    Parameters:
    - data: DataFrame containing Dubai housing data
    """
    st.header("Neighborhood Comparison Tool")
    st.write("Compare rental prices, amenities, and lifestyle factors across different Dubai neighborhoods.")
    
    # Get unique neighborhoods from data
    neighborhoods = sorted(data["neighborhood"].unique().tolist())
    
    # Allow user to select neighborhoods to compare (up to 4)
    st.subheader("Select Neighborhoods to Compare")
    col1, col2 = st.columns(2)
    
    with col1:
        neighborhood1 = st.selectbox("First Neighborhood", neighborhoods, index=0, key="nb1")
        neighborhood2 = st.selectbox("Second Neighborhood", neighborhoods, index=min(1, len(neighborhoods)-1), key="nb2")
    
    with col2:
        neighborhood3 = st.selectbox("Third Neighborhood (Optional)", ["None"] + neighborhoods, index=0, key="nb3")
        neighborhood4 = st.selectbox("Fourth Neighborhood (Optional)", ["None"] + neighborhoods, index=0, key="nb4")
    
    # Create a list of selected neighborhoods
    selected_neighborhoods = [neighborhood1, neighborhood2]
    if neighborhood3 != "None":
        selected_neighborhoods.append(neighborhood3)
    if neighborhood4 != "None":
        selected_neighborhoods.append(neighborhood4)
    
    # Property type filter
    property_types = ["All"] + sorted(data["property_type"].unique().tolist())
    selected_property_type = st.selectbox("Property Type", property_types, key="comp_prop_type")
    
    # Bedrooms filter
    bedroom_options = ["All", "Studio", "1 BR", "2 BR", "3+ BR"]
    selected_bedrooms = st.selectbox("Bedrooms", bedroom_options, key="comp_bedrooms")
    
    # Filter data for comparison
    filtered_data = data.copy()
    
    if selected_property_type != "All":
        filtered_data = filtered_data[filtered_data["property_type"] == selected_property_type]
    
    if selected_bedrooms != "All":
        if selected_bedrooms == "Studio":
            filtered_data = filtered_data[filtered_data["bedrooms"] == 0]
        elif selected_bedrooms == "1 BR":
            filtered_data = filtered_data[filtered_data["bedrooms"] == 1]
        elif selected_bedrooms == "2 BR":
            filtered_data = filtered_data[filtered_data["bedrooms"] == 2]
        elif selected_bedrooms == "3+ BR":
            filtered_data = filtered_data[filtered_data["bedrooms"] >= 3]
    
    # Filter for selected neighborhoods
    neighborhood_data = filtered_data[filtered_data["neighborhood"].isin(selected_neighborhoods)]
    
    # If there's no data for some neighborhoods, inform the user
    missing_neighborhoods = [n for n in selected_neighborhoods if n not in neighborhood_data["neighborhood"].unique()]
    if missing_neighborhoods:
        st.warning(f"No data available for the following neighborhoods with the current filters: {', '.join(missing_neighborhoods)}")
    
    # Create tabs for different comparison aspects
    tab1, tab2, tab3 = st.tabs(["Price Comparison", "Affordability Index", "Amenities & Lifestyle"])
    
    with tab1:
        st.subheader("Rental Price Comparison")
        
        if len(neighborhood_data) > 0:
            # Calculate average and median prices per neighborhood
            price_comparison = (
                neighborhood_data.groupby("neighborhood")
                .agg({
                    "price_yearly_aed": ["mean", "median", "min", "max", "count"],
                    "price_per_sqft": ["mean", "median"] if "price_per_sqft" in neighborhood_data.columns else ["mean"]
                })
            )
            
            # Flatten the column names
            price_comparison.columns = [f"{x}_{y}" for x, y in price_comparison.columns]
            price_comparison = price_comparison.reset_index()
            
            # Bar chart comparing average prices
            fig = px.bar(
                price_comparison,
                x="neighborhood",
                y="price_yearly_aed_mean",
                title="Average Yearly Rental Prices",
                labels={"price_yearly_aed_mean": "Average Yearly Rent (AED)", "neighborhood": "Neighborhood"},
                color="neighborhood",
                text_auto='.0f'
            )
            
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed price metrics in a table
            price_comparison_display = price_comparison.copy()
            price_comparison_display = price_comparison_display.rename(columns={
                "price_yearly_aed_mean": "Average (AED/year)",
                "price_yearly_aed_median": "Median (AED/year)",
                "price_yearly_aed_min": "Minimum (AED/year)",
                "price_yearly_aed_max": "Maximum (AED/year)",
                "price_yearly_aed_count": "Available Properties",
                "price_per_sqft_mean": "Avg Price/sqft (AED)" if "price_per_sqft_mean" in price_comparison_display.columns else ""
            })
            
            # Format numbers
            for col in price_comparison_display.columns:
                if col != "neighborhood" and col != "Available Properties":
                    price_comparison_display[col] = price_comparison_display[col].apply(lambda x: f"{int(x):,}")
            
            # Select and order columns
            columns_to_display = ["neighborhood", "Average (AED/year)", "Median (AED/year)", 
                                 "Minimum (AED/year)", "Maximum (AED/year)"]
            
            if "Avg Price/sqft (AED)" in price_comparison_display.columns:
                columns_to_display.append("Avg Price/sqft (AED)")
                
            columns_to_display.append("Available Properties")
            
            st.dataframe(price_comparison_display[columns_to_display], hide_index=True)
            
            # Price distribution by property type
            if "property_type" in neighborhood_data.columns and len(neighborhood_data["property_type"].unique()) > 1:
                st.subheader("Price by Property Type")
                
                property_type_comparison = (
                    neighborhood_data.groupby(["neighborhood", "property_type"])
                    .agg({"price_yearly_aed": "mean"})
                    .reset_index()
                )
                
                fig = px.bar(
                    property_type_comparison,
                    x="neighborhood",
                    y="price_yearly_aed",
                    color="property_type",
                    barmode="group",
                    title="Average Yearly Rent by Property Type",
                    labels={"price_yearly_aed": "Average Yearly Rent (AED)", 
                            "neighborhood": "Neighborhood",
                            "property_type": "Property Type"}
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected neighborhoods with the current filters. Please adjust your criteria.")
    
    with tab2:
        st.subheader("Affordability Index")
        
        # Create a slider for the user to input their annual income
        annual_income = st.slider(
            "Your Annual Income (AED)",
            min_value=50000,
            max_value=1000000,
            value=200000,
            step=10000,
            format="%d"
        )
        
        # Calculate affordability metrics
        # Usually, housing should be no more than 30% of income for affordability
        affordable_yearly_rent = annual_income * 0.3
        
        st.write(f"Based on the 30% rule, your affordable yearly rent would be approximately **{affordable_yearly_rent:,.0f} AED**.")
        
        if len(neighborhood_data) > 0:
            # Calculate affordability index for each neighborhood
            affordability_data = []
            
            for neighborhood in selected_neighborhoods:
                nb_data = neighborhood_data[neighborhood_data["neighborhood"] == neighborhood]
                
                if len(nb_data) > 0:
                    avg_price = nb_data["price_yearly_aed"].mean()
                    affordability_ratio = avg_price / affordable_yearly_rent
                    affordability_status = "Affordable" if affordability_ratio <= 1 else "Unaffordable"
                    affordability_score = max(0, min(100, int((1 - (affordability_ratio - 1)) * 100))) if affordability_ratio > 1 else 100
                    
                    # Percentage of properties within budget
                    within_budget = (nb_data["price_yearly_aed"] <= affordable_yearly_rent).mean() * 100
                    
                    affordability_data.append({
                        "neighborhood": neighborhood,
                        "avg_price": avg_price,
                        "affordability_ratio": affordability_ratio,
                        "affordability_status": affordability_status,
                        "affordability_score": affordability_score,
                        "within_budget_pct": within_budget
                    })
            
            affordability_df = pd.DataFrame(affordability_data)
            
            if len(affordability_df) > 0:
                # Create gauge charts for affordability score
                cols = st.columns(len(affordability_df))
                
                for i, (_, row) in enumerate(affordability_df.iterrows()):
                    with cols[i]:
                        # Create gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=row["affordability_score"],
                            title={"text": row["neighborhood"]},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "#E6B800"},
                                "steps": [
                                    {"range": [0, 30], "color": "red"},
                                    {"range": [30, 70], "color": "orange"},
                                    {"range": [70, 100], "color": "green"}
                                ],
                                "threshold": {
                                    "line": {"color": "black", "width": 4},
                                    "thickness": 0.75,
                                    "value": row["affordability_score"]
                                }
                            }
                        ))
                        
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.metric(
                            "Average Yearly Rent",
                            f"{int(row['avg_price']):,} AED",
                            f"{'-' if row['affordability_ratio'] > 1 else '+'}{abs(row['affordability_ratio'] - 1) * 100:.1f}% {'above' if row['affordability_ratio'] > 1 else 'below'} budget"
                        )
                        
                        st.write(f"Properties within budget: **{row['within_budget_pct']:.1f}%**")
                
                # Bar chart showing percentage of properties within budget
                fig = px.bar(
                    affordability_df,
                    x="neighborhood",
                    y="within_budget_pct",
                    title="Percentage of Properties Within Your Budget",
                    labels={"within_budget_pct": "Properties Within Budget (%)", "neighborhood": "Neighborhood"},
                    color="neighborhood",
                    text_auto='.1f'
                )
                
                fig.update_traces(textposition="outside")
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Could not calculate affordability metrics with the current data.")
        else:
            st.warning("No data available for the selected neighborhoods with the current filters. Please adjust your criteria.")
    
    with tab3:
        st.subheader("Amenities & Lifestyle Comparison")
        
        # This would ideally come from real data about neighborhoods
        # For now, we'll use the constant data from constants.py
        
        lifestyle_data = []
        
        for neighborhood in selected_neighborhoods:
            if neighborhood in NEIGHBORHOOD_INFO:
                lifestyle_data.append(NEIGHBORHOOD_INFO[neighborhood])
            else:
                # Create placeholder data if not in constants
                lifestyle_data.append({
                    "neighborhood": neighborhood,
                    "commute_time": np.random.randint(10, 45),
                    "schools_rating": np.random.randint(1, 5),
                    "shopping_rating": np.random.randint(1, 5),
                    "dining_rating": np.random.randint(1, 5),
                    "parks_rating": np.random.randint(1, 5),
                    "metro_access": np.random.choice([True, False]),
                    "beach_access": np.random.choice([True, False]),
                    "lifestyle": np.random.choice(["Family", "Singles", "Mixed"]),
                    "parking_availability": np.random.choice(["Limited", "Adequate", "Abundant"])
                })
        
        lifestyle_df = pd.DataFrame(lifestyle_data)
        
        # Radar chart for ratings
        categories = ["Commute Time", "Schools", "Shopping", "Dining", "Parks"]
        
        fig = go.Figure()
        
        for _, row in lifestyle_df.iterrows():
            # Normalize commute time (lower is better)
            commute_normalized = 5 - min(5, row["commute_time"] / 10)
            
            fig.add_trace(go.Scatterpolar(
                r=[commute_normalized, row["schools_rating"], row["shopping_rating"], 
                   row["dining_rating"], row["parks_rating"]],
                theta=categories,
                fill='toself',
                name=row["neighborhood"]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            title="Lifestyle & Amenities Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a comparison table
        comparison_table = lifestyle_df.copy()
        comparison_table = comparison_table.rename(columns={
            "commute_time": "Avg. Commute Time (min)",
            "schools_rating": "Schools (1-5)",
            "shopping_rating": "Shopping (1-5)",
            "dining_rating": "Dining (1-5)",
            "parks_rating": "Parks (1-5)",
            "metro_access": "Metro Access",
            "beach_access": "Beach Access",
            "lifestyle": "Lifestyle",
            "parking_availability": "Parking"
        })
        
        # Format boolean values
        comparison_table["Metro Access"] = comparison_table["Metro Access"].apply(lambda x: "✅" if x else "❌")
        comparison_table["Beach Access"] = comparison_table["Beach Access"].apply(lambda x: "✅" if x else "❌")
        
        st.dataframe(comparison_table[[
            "neighborhood", "Avg. Commute Time (min)", "Schools (1-5)", 
            "Shopping (1-5)", "Dining (1-5)", "Parks (1-5)",
            "Metro Access", "Beach Access", "Lifestyle", "Parking"
        ]], hide_index=True)
        
        # Neighborhood descriptions
        st.subheader("Neighborhood Descriptions")
        
        for neighborhood in selected_neighborhoods:
            if neighborhood in NEIGHBORHOOD_INFO and "description" in NEIGHBORHOOD_INFO[neighborhood]:
                st.write(f"**{neighborhood}**: {NEIGHBORHOOD_INFO[neighborhood]['description']}")
            else:
                st.write(f"**{neighborhood}**: Detailed description not available.")
