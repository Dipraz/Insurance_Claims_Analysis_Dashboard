import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load and apply custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load and apply the CSS
load_css()
# Load and prepare the data
@st.cache_resource
def load_data():
    data = pd.read_csv("combined_data.csv")
    data['Date'] = pd.to_datetime(data['DateID'], unit='s')
    return data

df = load_data()
# Dashboard layout and design
st.title("Insurance Claims Analysis Dashboard")

# User interface and navigation
st.sidebar.header("Filters and Adjustments")

# Date range filter
date_range_start = pd.to_datetime(st.sidebar.date_input("Select Start Date", df["Date"].min()))
date_range_end = pd.to_datetime(st.sidebar.date_input("Select End Date", df["Date"].max()))
filtered_df = df[(df["Date"] >= date_range_start) & (df["Date"] <= date_range_end)]

# Analysis selection
analysis_selection = st.sidebar.selectbox("Select Analysis Type:", [
    "Total Claims Over Time",
    "Difference Calculation",
    "Regional Map",
    "Top 10 Cities",
    "Threshold Adjustments",
    "Customer and Property Insights"
])
# Total Claims Over Time
if analysis_selection == "Total Claims Over Time":
    st.subheader("Total Number of Claims Over Time")
    chart_type = st.selectbox("Select Chart Type", ["Line", "Bar", "Pie"])
    claim_type_filter = st.multiselect("Filter by Claim Type", df['ClaimType'].unique())
    
    # Apply the claim type filter
    if claim_type_filter:
        filtered_df = filtered_df[filtered_df['ClaimType'].isin(claim_type_filter)]
    
    time_aggregation = st.selectbox("Select Time Aggregation:", ["Year", "Month", "Week", "Day"])

    # Aggregation logic for Line and Bar charts
    if chart_type in ["Line", "Bar"]:
        if time_aggregation == "Year":
            temp_df = filtered_df.copy()
            temp_df['Year'] = temp_df['Date'].dt.year
            aggregated_data = temp_df.groupby('Year').size().reset_index(name='Count')
            x_axis = 'Year'
        elif time_aggregation == "Month":
            temp_df = filtered_df.copy()
            temp_df['Month'] = temp_df['Date'].dt.to_period('M').astype(str)  # Convert to string
            aggregated_data = temp_df.groupby('Month').size().reset_index(name='Count')
            x_axis = 'Month'
        elif time_aggregation == "Week":
            temp_df = filtered_df.copy()
            temp_df['Week'] = temp_df['Date'].dt.to_period('W').astype(str)  # Convert to string
            aggregated_data = temp_df.groupby('Week').size().reset_index(name='Count')
            x_axis = 'Week'
        else:  # Day
            temp_df = filtered_df.copy()
            temp_df['Day'] = temp_df['Date'].dt.to_period('D').astype(str)  # Convert to string
            aggregated_data = temp_df.groupby('Day').size().reset_index(name='Count')
            x_axis = 'Day'

        fig = px.line(aggregated_data, x=x_axis, y='Count') if chart_type == "Line" else px.bar(aggregated_data, x=x_axis, y='Count')

    # Aggregation logic for Pie chart
    elif chart_type == "Pie":
        aggregated_data = filtered_df['ClaimType'].value_counts().reset_index(name='Count')
        aggregated_data.rename(columns={'index': 'ClaimType'}, inplace=True)
        fig = px.pie(aggregated_data, names='ClaimType', values='Count', title='Distribution of Claim Types')

    st.plotly_chart(fig)
elif analysis_selection == "Difference Calculation":
    st.subheader("Difference Calculation Based on Dimensions")

    # Select dimension type
    dimension_type = st.radio("Select Dimension Type", ["Categorical", "Numeric"])

    # Select the dimension based on the chosen type
    if dimension_type == "Categorical":
        dimension = st.selectbox("Select Categorical Dimension:", df.select_dtypes(include=['object']).columns)
        fig = px.bar(filtered_df, x=dimension, title=f"Distribution of Claims by {dimension}")
    else:
        dimension = st.selectbox("Select Numeric Dimension:", df.select_dtypes(include=['int64', 'float64']).columns)
        fig = px.histogram(filtered_df, x=dimension, title=f"Distribution of Claims by {dimension}")

    # Plot the figure
    st.plotly_chart(fig)

    # Display statistical summary if the dimension is numeric
    if dimension_type == "Numeric":
        st.write(f"Mean of {dimension}: {filtered_df[dimension].mean()}")
        st.write(f"Median of {dimension}: {filtered_df[dimension].median()}")
        st.write(f"Total Count for {dimension}: {filtered_df[dimension].count()}")
    
elif analysis_selection == "Regional Map":
    st.subheader("Regional Distribution of Claims")

    # Assigning approximate coordinates for each region
    region_coords = {
        'West': {'lat': 51.5000, 'lon': -5.5000},
        'North': {'lat': 55.0000, 'lon': -2.0000},
        'East': {'lat': 52.5000, 'lon': 0.5000},
        'Central': {'lat': 52.4858, 'lon': -1.8904},
        'South': {'lat': 51.0000, 'lon': -0.1167}
    }

    # Interactive filters
    claim_type_filter = st.sidebar.multiselect('Select Claim Types', df['ClaimType'].unique())
    filtered_df = df[df['ClaimType'].isin(claim_type_filter)] if claim_type_filter else df

    # Add latitude and longitude to the DataFrame based on the region
    filtered_df['lat'] = filtered_df['Region'].apply(lambda x: region_coords[x]['lat'])
    filtered_df['lon'] = filtered_df['Region'].apply(lambda x: region_coords[x]['lon'])

    # Aggregate claim amounts and other metrics by region
    regional_data = filtered_df.groupby('Region').agg({
        'ClaimAmount': 'sum',
        'lat': 'first',
        'lon': 'first',
        'CustomerID': 'count',  # Total number of claims
        'ClaimAmount': 'mean'  # Average claim amount
    }).reset_index()

    # Create a scatter map with enhanced hover data
    fig = px.scatter_mapbox(regional_data, lat='lat', lon='lon', size='ClaimAmount', hover_name='Region', 
                            hover_data={'CustomerID': ':.0f', 'ClaimAmount': ':.2f'},
                            color_continuous_scale="Viridis", zoom=5)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig)
# Top 10 Cities
elif analysis_selection == "Top 10 Cities":
    st.subheader("Top 10 Cities with Highest Claims")

    # Display the top cities by total claim amount
    top_cities_df = df.groupby('City')['ClaimAmount'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_cities_df)

    selected_city = st.selectbox("Select City:", top_cities_df.index)

    # Filter the data for the selected city
    city_df = filtered_df[filtered_df['City'] == selected_city]

    # Interactive chart showing claims by property type in the selected city
    fig = px.bar(city_df, x='PropertyType', y='ClaimAmount',
                 title=f"Claims in {selected_city} by Property Type",
                 color='PropertyType', barmode='group')
    st.plotly_chart(fig)
    # Display statistical insights about the selected city
    st.write(f"Total Claims in {selected_city}: {city_df['ClaimAmount'].sum():,.2f}")
    st.write(f"Average Claim Amount in {selected_city}: {city_df['ClaimAmount'].mean():,.2f}")
    st.write(f"Highest Claim in {selected_city}: {city_df['ClaimAmount'].max():,.2f}")
    most_common_claim_type = city_df['ClaimType'].mode()[0]
    st.write(f"Most Common Claim Type in {selected_city}: {most_common_claim_type}")


    # Extract necessary information
    property_types = city_df['PropertyType'].tolist()
    claim_amounts = city_df['ClaimAmount'].apply(lambda x: f"${x:,.0f}").tolist()

    # Correct hovertemplate with extracted information
    fig.update_traces(hovertemplate=f"Property Type: %{property_types}<br>Claim Amount: %{claim_amounts}")
    st.plotly_chart(fig)
    # Additional informative metrics
    st.metric("Total Claims in City:", city_df['ClaimAmount'].sum())
    st.metric("Average Claim Amount:", city_df['ClaimAmount'].mean())
    st.metric("Highest Claim Amount:", city_df['ClaimAmount'].max())
    # Explore other dimensions interactively
    other_dimension = st.selectbox("Explore by Another Dimension:", ["Claim Type", "Customer Segment", "Risk Tolerance"])
    if other_dimension:
        # Modify other_dimension to handle spaces
        other_dimension_column = other_dimension.replace(" ", "")
        # Create a suitable plot based on the selected dimension
        fig = px.bar(city_df, x=other_dimension_column, y='ClaimAmount', title=f"Claims in {selected_city} by {other_dimension}")
        st.plotly_chart(fig)
# Threshold Adjustments
elif analysis_selection == "Threshold Adjustments":
    st.subheader("Threshold Value Setting")
    claim_threshold = st.slider("Claim Amount Threshold:", 0, int(filtered_df['ClaimAmount'].max()), 5000)
    threshold_df = filtered_df[filtered_df['ClaimAmount'] > claim_threshold]
    st.write(threshold_df)

# Customer and Property Insights
elif analysis_selection == "Customer and Property Insights":
    st.subheader("Customer and Property Insights Panels")
    st.metric("Average Claim Amount", filtered_df['ClaimAmount'].mean())
    st.metric("Most Common Claim Type", filtered_df['ClaimType'].mode()[0])
    property_insight = st.selectbox("Choose Property Insight:", ['PropertyType', 'AgeOfProperty'])
    fig = px.histogram(filtered_df, x=property_insight, title=f"Distribution by {property_insight}")
    st.plotly_chart(fig)
