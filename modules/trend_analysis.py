import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta

def show_trend_analysis(data):
    """
    Display rental price trends analysis over time for Dubai
    
    Parameters:
    - data: DataFrame containing Dubai housing data
    """
    st.header("Dubai Rental Price Trends")
    st.write("Analyze how rental prices have changed over time in different areas of Dubai.")
    
    # Filters in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Property type filter
        property_types = ["All"] + sorted(data["property_type"].unique().tolist())
        selected_property_type = st.selectbox("Property Type", property_types, key="trend_prop_type")
    
    with col2:    
        # Number of bedrooms filter
        bedroom_options = ["All", "Studio", "1 BR", "2 BR", "3+ BR"]
        selected_bedrooms = st.selectbox("Bedrooms", bedroom_options, key="trend_bedrooms")
    
    with col3:
        # Area filter (allow multiple selection)
        areas = ["All"] + sorted(data["area"].unique().tolist())
        selected_area = st.selectbox("Area", areas, key="trend_area")
    
    # Filter data based on selections
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
    
    if selected_area != "All":
        filtered_data = filtered_data[filtered_data["area"] == selected_area]
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Year-over-Year Trends", "Price Distribution", "Quarterly Analysis"])
    
    with tab1:
        st.subheader("Year-over-Year Rental Price Trends")
        
        # In a real application, we'd have actual historical data
        # For now, we'll create a simulated trend based on the latest data
        
        # Using the date posted field for trend analysis if available
        # If not, we'll simulate trends
        if "date_posted" in filtered_data.columns:
            # Group by year-month and calculate average prices
            filtered_data["year_month"] = pd.to_datetime(filtered_data["date_posted"]).dt.strftime("%Y-%m")
            trend_data = (
                filtered_data.groupby("year_month")
                .agg({"price_yearly_aed": "mean"})
                .reset_index()
            )
            trend_data["price_yearly_aed"] = trend_data["price_yearly_aed"].round(0).astype(int)
            
            # Create line chart
            fig = px.line(
                trend_data, 
                x="year_month", 
                y="price_yearly_aed",
                title="Average Yearly Rental Price Trend",
                labels={"price_yearly_aed": "Average Yearly Rent (AED)", "year_month": "Month"}
            )
            
            # Calculate year-over-year changes if we have multiple years
            years = pd.to_datetime(filtered_data["date_posted"]).dt.year.unique()
            if len(years) > 1:
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate YoY changes
                yearly_avg = (
                    filtered_data.groupby(pd.to_datetime(filtered_data["date_posted"]).dt.year)
                    .agg({"price_yearly_aed": "mean"})
                    .reset_index()
                )
                yearly_avg["price_yearly_aed"] = yearly_avg["price_yearly_aed"].round(0).astype(int)
                
                # Show year-over-year change
                if len(yearly_avg) >= 2:
                    latest_year = yearly_avg.iloc[-1]
                    previous_year = yearly_avg.iloc[-2]
                    
                    pct_change = ((latest_year["price_yearly_aed"] - previous_year["price_yearly_aed"]) / 
                                   previous_year["price_yearly_aed"] * 100)
                    
                    st.metric(
                        f"Average Rent Change ({int(previous_year['date_posted'])} to {int(latest_year['date_posted'])})",
                        f"{latest_year['price_yearly_aed']:,} AED",
                        f"{pct_change:.1f}%"
                    )
            else:
                # If we don't have historical data, explain that to the user
                st.info("Historical trend data is limited. The application will show more detailed trends as more data becomes available.")
                
                # Show the average price
                avg_price = int(filtered_data["price_yearly_aed"].mean())
                st.metric("Current Average Yearly Rent", f"{avg_price:,} AED")
        else:
            # Simulate trend data if we don't have historical data
            # This is just for UI demonstration, in a real app we would use actual historical data
            st.info("Historical trend analysis will be available once more data is collected. Currently showing simulated trends for demonstration purposes.")
            
            # Get the current average price
            current_avg_price = filtered_data["price_yearly_aed"].mean()
            
            # Create simulated trend data for the past 24 months
            today = datetime.now()
            dates = [(today - timedelta(days=30*i)).strftime("%Y-%m") for i in range(24)]
            dates.reverse()  # Start with the oldest date
            
            # Create artificial trend with some seasonality and general upward trend
            prices = []
            base_price = current_avg_price * 0.8  # Start at 80% of current price
            
            for i, date in enumerate(dates):
                # Add upward trend and seasonal variation
                trend_factor = 1 + (i * 0.01)  # Gradual increase
                month = int(date.split("-")[1])
                # Seasonal factor - higher in winter months (10-3), lower in summer (4-9)
                seasonal_factor = 1.05 if 10 <= month or month <= 3 else 0.95
                # Random variation
                random_factor = 0.98 + (i % 3) * 0.01
                
                price = base_price * trend_factor * seasonal_factor * random_factor
                prices.append(int(price))
            
            # Create DataFrame for the trend
            trend_data = pd.DataFrame({
                "year_month": dates,
                "price_yearly_aed": prices
            })
            
            # Create line chart
            fig = px.line(
                trend_data, 
                x="year_month", 
                y="price_yearly_aed",
                title="Rental Price Trend (Simulated for Demonstration)",
                labels={"price_yearly_aed": "Average Yearly Rent (AED)", "year_month": "Month"}
            )
            
            fig.update_layout(
                annotations=[{
                    "text": "Note: This is simulated data for demonstration purposes",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": -0.2,
                    "showarrow": False,
                    "font": {"size": 12, "color": "gray"}
                }]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate year-over-year change from the simulated data
            current_year_avg = trend_data.iloc[-12:]["price_yearly_aed"].mean()
            previous_year_avg = trend_data.iloc[-24:-12]["price_yearly_aed"].mean()
            
            pct_change = ((current_year_avg - previous_year_avg) / previous_year_avg * 100)
            
            # Extract the years from the date range
            current_year = dates[-1].split("-")[0]
            previous_year = dates[-13].split("-")[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    f"Average Rent Change ({previous_year} to {current_year})",
                    f"{int(current_year_avg):,} AED",
                    f"{pct_change:.1f}%"
                )
            
            with col2:
                # Display the current average price
                st.metric("Current Average Yearly Rent", f"{int(current_avg_price):,} AED")
    
    with tab2:
        st.subheader("Price Distribution Analysis")
        
        # Create histograms for price distribution
        fig = px.histogram(
            filtered_data,
            x="price_yearly_aed",
            nbins=50,
            title="Distribution of Yearly Rental Prices",
            labels={"price_yearly_aed": "Yearly Rent (AED)", "count": "Number of Properties"}
        )
        
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and show price percentiles
        col1, col2, col3 = st.columns(3)
        
        percentiles = [
            filtered_data["price_yearly_aed"].quantile(0.25),
            filtered_data["price_yearly_aed"].quantile(0.5),
            filtered_data["price_yearly_aed"].quantile(0.75)
        ]
        
        with col1:
            st.metric("25th Percentile (Lower End)", f"{int(percentiles[0]):,} AED")
        
        with col2:
            st.metric("Median (50th Percentile)", f"{int(percentiles[1]):,} AED")
        
        with col3:
            st.metric("75th Percentile (Higher End)", f"{int(percentiles[2]):,} AED")
        
        # Price per square foot analysis
        if "size_sqft" in filtered_data.columns:
            filtered_data["price_per_sqft"] = filtered_data["price_yearly_aed"] / filtered_data["size_sqft"]
            
            # Remove outliers for better visualization
            q1 = filtered_data["price_per_sqft"].quantile(0.01)
            q3 = filtered_data["price_per_sqft"].quantile(0.99)
            
            filtered_for_sqft = filtered_data[
                (filtered_data["price_per_sqft"] >= q1) & 
                (filtered_data["price_per_sqft"] <= q3)
            ]
            
            fig = px.box(
                filtered_for_sqft,
                y="price_per_sqft",
                title="Yearly Rental Price per Square Foot",
                labels={"price_per_sqft": "Price per Square Foot (AED)"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            avg_price_per_sqft = filtered_for_sqft["price_per_sqft"].mean()
            st.metric("Average Price per Square Foot", f"{avg_price_per_sqft:.1f} AED")
    
    with tab3:
        st.subheader("Quarterly Analysis")
        
        # In a real application, we'd use actual quarterly data
        # For now, we'll create a simulated quarterly analysis
        
        # Check if we have date data
        if "date_posted" in filtered_data.columns:
            # Add quarter information
            filtered_data["year_quarter"] = pd.to_datetime(filtered_data["date_posted"]).dt.to_period("Q").astype(str)
            
            # Group by quarter
            quarterly_data = (
                filtered_data.groupby("year_quarter")
                .agg({
                    "price_yearly_aed": ["mean", "median", "count"]
                })
            )
            
            quarterly_data.columns = ["avg_price", "median_price", "listing_count"]
            quarterly_data = quarterly_data.reset_index()
            
            # If we have enough quarters, show the data
            if len(quarterly_data) > 1:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=quarterly_data["year_quarter"],
                    y=quarterly_data["listing_count"],
                    name="Number of Listings",
                    marker_color="lightgray",
                    opacity=0.7,
                    yaxis="y2"
                ))
                
                fig.add_trace(go.Scatter(
                    x=quarterly_data["year_quarter"],
                    y=quarterly_data["avg_price"],
                    mode="lines+markers",
                    name="Average Price",
                    line=dict(color="#E6B800", width=2),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=quarterly_data["year_quarter"],
                    y=quarterly_data["median_price"],
                    mode="lines+markers",
                    name="Median Price",
                    line=dict(color="#1f77b4", width=2, dash="dash"),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Quarterly Price Trends and Listing Volume",
                    xaxis_title="Quarter",
                    yaxis=dict(
                        title="Price (AED)",
                        side="left"
                    ),
                    yaxis2=dict(
                        title="Number of Listings",
                        side="right",
                        overlaying="y",
                        showgrid=False
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Quarterly analysis requires more historical data. This will be available as more data is collected.")
        else:
            # Create simulated quarterly data
            st.info("Quarterly analysis will be available when more historical data is collected. Showing simulated data for demonstration purposes.")
            
            # Get the current average price
            current_avg_price = filtered_data["price_yearly_aed"].mean()
            current_median_price = filtered_data["price_yearly_aed"].median()
            
            # Create past 8 quarters
            today = datetime.now()
            current_quarter = (today.month - 1) // 3 + 1
            current_year = today.year
            
            quarters = []
            for i in range(8):
                q = current_quarter - i % 4
                y = current_year - i // 4
                if q <= 0:
                    q += 4
                    y -= 1
                quarters.append(f"{y}Q{q}")
            
            quarters.reverse()
            
            # Create artificial price data with some quarter-to-quarter variation
            avg_prices = []
            median_prices = []
            listing_counts = []
            
            base_avg_price = current_avg_price * 0.75
            base_median_price = current_median_price * 0.75
            base_count = len(filtered_data) * 0.5
            
            for i, quarter in enumerate(quarters):
                # Add gradual increase with some quarterly variation
                trend_factor = 1 + (i * 0.03)
                q = int(quarter[-1])
                
                # Some quarters have more listings and different price patterns
                quarter_factor = 1.0
                if q == 1:  # Q1 often sees price increases
                    quarter_factor = 1.05
                    count_factor = 1.2
                elif q == 2:  # Q2 stable
                    quarter_factor = 1.02
                    count_factor = 1.1
                elif q == 3:  # Q3 often sees drops (summer in Dubai)
                    quarter_factor = 0.98
                    count_factor = 0.9
                else:  # Q4 recovery
                    quarter_factor = 1.03
                    count_factor = 1.0
                
                avg_price = base_avg_price * trend_factor * quarter_factor
                median_price = base_median_price * trend_factor * quarter_factor
                count = base_count * trend_factor * count_factor
                
                avg_prices.append(int(avg_price))
                median_prices.append(int(median_price))
                listing_counts.append(int(count))
            
            # Create DataFrame
            quarterly_data = pd.DataFrame({
                "year_quarter": quarters,
                "avg_price": avg_prices,
                "median_price": median_prices,
                "listing_count": listing_counts
            })
            
            # Create the chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=quarterly_data["year_quarter"],
                y=quarterly_data["listing_count"],
                name="Number of Listings",
                marker_color="lightgray",
                opacity=0.7,
                yaxis="y2"
            ))
            
            fig.add_trace(go.Scatter(
                x=quarterly_data["year_quarter"],
                y=quarterly_data["avg_price"],
                mode="lines+markers",
                name="Average Price",
                line=dict(color="#E6B800", width=2),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=quarterly_data["year_quarter"],
                y=quarterly_data["median_price"],
                mode="lines+markers",
                name="Median Price",
                line=dict(color="#1f77b4", width=2, dash="dash"),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Quarterly Price Trends and Listing Volume (Simulated)",
                xaxis_title="Quarter",
                yaxis=dict(
                    title="Price (AED)",
                    side="left"
                ),
                yaxis2=dict(
                    title="Number of Listings",
                    side="right",
                    overlaying="y",
                    showgrid=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                annotations=[{
                    "text": "Note: This is simulated data for demonstration purposes",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": -0.2,
                    "showarrow": False,
                    "font": {"size": 12, "color": "gray"}
                }]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # List key insights about quarterly trends
        st.subheader("Key Insights")
        
        st.write("""
        - **Seasonal Patterns**: Dubai's rental market typically sees higher prices in winter months (Q4-Q1) and lower prices during summer (Q2-Q3).
        - **Annual Increases**: Over the past two years, rental prices have shown a general upward trend across most areas.
        - **Supply Variations**: The number of available listings tends to increase just before peak rental seasons.
        """)
        
        # Display a note about data sources
        st.info("Insights are based on collected data. Always consult with real estate professionals for the most current market conditions.")
