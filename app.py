import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set the page configuration to give a title and layout
st.set_page_config(page_title="Claim Tracking Dashboard", layout="wide")

# Function to load and cache data for better performance
@st.cache_data
def load_data():
    data = pd.read_csv("combined_data.csv")
    data['Date'] = pd.to_datetime(data['DateID'], unit='s')
    return data

df = load_data()

# Function to create a DataFrame from the city coordinates
def create_city_coordinates_df():
    city_coordinates = {
        "City": ["London", "Birmingham", "Glasgow", "Liverpool", "Manchester", "Edinburgh", "Leeds", "Bradford", "Sheffield"],
        "Latitude": [51.509865, 52.489471, 55.860916, 53.400002, 53.483959, 55.953251, 53.801277, 53.799999, 53.801277],
        "Longitude": [-0.118092, -1.898575, -4.251433, -2.983333, -2.244644, -3.188267, -1.548567, -1.750000, -1.548567]
    }
    return pd.DataFrame(city_coordinates)

city_coordinates_df = create_city_coordinates_df()
filtered_df = pd.merge(df, city_coordinates_df, on='City', how='left')

# Header with logo and title
st.image("logo.jpg", width=100)
st.title("Claim Tracking Dashboard 🚀")

# Sidebar filters
with st.sidebar:
    st.header("Filters 🎛️")
    date_range = st.date_input("Select Date Range 📅", [])
    selected_cities = st.multiselect("Select Cities 🏙️", options=filtered_df['City'].unique())
    selected_marital_statuses = st.multiselect("Select Marital Statuses 💍", options=filtered_df['MaritalStatus'].unique())
    selected_claim_types = st.multiselect("Select Claim Types 📑", options=filtered_df['ClaimType'].unique())
    selected_property_types = st.multiselect("Select Property Types 🏠", options=filtered_df['PropertyType'].unique())
    selected_occupations = st.multiselect("Select Occupations 👩‍💼", options=filtered_df['Occupation'].unique())

# Apply filters
conditions = []  # List to hold all filtering conditions
if date_range:
    conditions.append(filtered_df['Date'].between(*date_range))
if selected_cities:
    conditions.append(filtered_df['City'].isin(selected_cities))
if selected_marital_statuses:
    conditions.append(filtered_df['MaritalStatus'].isin(selected_marital_statuses))
if selected_claim_types:
    conditions.append(filtered_df['ClaimType'].isin(selected_claim_types))
if selected_property_types:
    conditions.append(filtered_df['PropertyType'].isin(selected_property_types))
if selected_occupations:
    conditions.append(filtered_df['Occupation'].isin(selected_occupations))
# Apply all conditions for filtering
if conditions:
    filtered_df = filtered_df[np.logical_and.reduce(conditions)]
    
# KPI Metrics with Time Series Line Chart
def display_kpi_metrics(data):
    st.header("KPI Metrics")
    fig_kpi = px.line(data.groupby('Date')['ClaimAmount'].sum(), x=data.groupby('Date')['ClaimAmount'].sum().index, y='ClaimAmount',
                      labels={'x': 'Date', 'y': 'Total Claim Amount'}, title='Total Claims Over Time')
    st.plotly_chart(fig_kpi, use_container_width=True)

    kpi_cols = st.columns(3)
    kpi_names = ["Total Claims 💰", "Average Claim Amount 💹", "Claims Change 📉"]
    kpi_values = [data['ClaimAmount'].sum(), data['ClaimAmount'].mean(), data['ClaimAmount'].sum() - df['ClaimAmount'].sum()]

    for col, kpi_name, kpi_value in zip(kpi_cols, kpi_names, kpi_values):
        col.metric(label=kpi_name, value=kpi_value)

display_kpi_metrics(filtered_df)
# KPI Metric cards
def display_kpi_cards(data):
    average_credit_score = data['CreditScore'].mean()
    low_risk_percentage = data['RiskTolerance'].value_counts(normalize=True).get('Low', 0) * 100

    # KPI card for Average Credit Score (Gauge chart)
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=average_credit_score,
        title={'text': "Average Credit Score"},
        gauge={'axis': {'range': [data['CreditScore'].min(), data['CreditScore'].max()]}}
    ))

    # KPI card for Low Risk Percentage (Donut chart)
    fig2 = px.pie(values=[low_risk_percentage, 100 - low_risk_percentage],
                  names=['Low Risk', 'High Risk'],
                  title='Low Risk Percentage',
                  hole=0.4)

    # Placing KPI cards in a horizontal layout
    kpi_cols = st.columns(2)
    with kpi_cols[0]:
        st.plotly_chart(fig1, use_container_width=True)
    with kpi_cols[1]:
        st.plotly_chart(fig2, use_container_width=True)

# Displaying the KPI cards
display_kpi_cards(filtered_df)
# Main Content with Various Charts
def display_main_charts(data):
    # Creating two layouts
    layout1 = st.columns(2)
    layout2 = st.columns(2)

# Main Content with Various Charts
def display_main_charts(data):
    layout1 = st.columns(2)
    layout2 = st.columns(2)

    # Chart 1: Bar chart for Claims by Customer Segment
    with layout1[0]:
        fig3 = px.bar(data, x='CustomerSegment', y='ClaimAmount', title='Claims by Customer Segment', color='CustomerSegment')
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 3: Bar chart for Claims by City
    with layout2[1]:
        top_cities = data.groupby('City')['ClaimAmount'].sum().sort_values(ascending=False).head(10).reset_index()
        fig5 = px.bar(top_cities, x='City', y='ClaimAmount', title='Top Cities by Claims', color='City')
        st.plotly_chart(fig5, use_container_width=True)

    # Chart 4: Donut chart for Claims by Property Type
    with layout2[0]:
        fig_property_type_donut = px.pie(data, names='PropertyType', title='Claims by Property Type', hole=0.4, color='PropertyType')
        st.plotly_chart(fig_property_type_donut, use_container_width=True)

    # Chart 2: Line chart for Claims Over Time
    with layout1[1]:
        fig4 = px.line(data, x='Date', y='ClaimAmount', title='Claims Over Time', color='ClaimType')
        st.plotly_chart(fig4, use_container_width=True)
# Chart 5: Bar chart for Total Claims Threshold
    total_claims_threshold_chart = px.bar(data, x='CustomerID', y='TotalClaimsThreshold', title='Total Claims Threshold')
    st.plotly_chart(total_claims_threshold_chart, use_container_width=True)
    # Check if layout2 has at least three elements
    if len(layout2) >= 3:
        # Add another layout for TotalClaimsThreshold
        total_claims_threshold_chart = px.bar(data, x='CustomerID', y='TotalClaimsThreshold', title='Total Claims Threshold')
        with layout2[2]:
            st.plotly_chart(total_claims_threshold_chart, use_container_width=True)

# Load data using the cache
df = load_data()

# Displaying the main charts with updated visualizations
display_main_charts(df)

# Claim Distribution Map
def display_claim_distribution_map(data):
    st.header("Claim Distribution Map 🗺️")
    color_variable = 'City' if st.checkbox("Color by City", True) else 'MaritalStatus'

    map_fig = px.scatter_mapbox(
        data,
        lat='Latitude',
        lon='Longitude',
        color=color_variable,
        size='ClaimAmount',
        hover_name='Name',
        title='Claim Distribution Map',
        mapbox_style="carto-positron",
        zoom=5
    )
    st.plotly_chart(map_fig, use_container_width=True)

display_claim_distribution_map(filtered_df)

# Footer with social media links
st.markdown("Connect with Us! 👋")
st.markdown("[![Twitter](https://img.shields.io/twitter/follow/your_twitter?style=social)](https://twitter.com/your_twitter)")
st.markdown("[![GitHub](https://img.shields.io/github/stars/your_repo?style=social)](https://github.com/your_repo)")
