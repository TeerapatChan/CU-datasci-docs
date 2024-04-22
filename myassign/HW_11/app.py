import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
st.title("Analysis of the Thailand Rain Daily Dataset")
st.write("This is a simple example of a Streamlit app that displays the Thailand Rain Daily dataset.")

@st.cache_data
def load_data():
    df = pd.read_csv("RainDaily_Tabular.csv")
    return df

# Load the dataset
df = load_data()
df['date'] = pd.to_datetime(df['date'])

# Get the unique values of the province and date columns
province = df['province'].unique()
date = df['date'].unique()

provinces = st.sidebar.multiselect("Select the provinces", province)

# Select all provinces
selectAll_provinces = st.sidebar.checkbox("Select all provinces", value=False)
if selectAll_provinces:
    provinces = province

start_date = st.sidebar.date_input("Select the start date", date[0])
end_date = st.sidebar.date_input("Select the end date", date[-1])

dates = pd.date_range(start_date, end_date)

# Display the dataset
st.write(df.head())

# Display the dataset description
st.subheader("The dataset has the following description:")
st.write(df.describe())

# Filter the dataset by selected provinces and dates
df_filtered = df[df['province'].isin(provinces)]
df_filtered = df_filtered[df_filtered['date'].isin(dates)]

# Display the filtered dataset
st.subheader("Average rain by selected dates for each selected province:")

# Plot the average rain by province

# Bar chart
if df_filtered.empty:
    st.write("No data available for the selected provinces and dates.")
else:
    fig = px.bar(df_filtered.groupby('province')['rain'].mean(), y='rain', title='Average rain by province').update_layout(
        xaxis_title="Province",
        yaxis_title="Average rain",
    )
    st.plotly_chart(fig)

# Line chart

if df_filtered.empty:
    st.write("No data available for the selected provinces and dates.")
else:
    # Create an empty list to store data for each province
    data_for_plot = []

    # Iterate over selected provinces
    for province in provinces:
        df_filtered_province = df_filtered[df_filtered['province'] == province]
        # Append data for this province to the list
        data_for_plot.append(df_filtered_province.groupby('date')['rain'].mean().rename(province))

    # Concatenate the data into a single DataFrame
    df_for_plot = pd.concat(data_for_plot, axis=1)

    # Plot using Streamlit's line chart
    fig = px.line(df_for_plot, title='Average rain by day for each selected province').update_layout(
        xaxis_title="Date",
        yaxis_title="Average rain",
    )
    st.plotly_chart(fig)

avg_rain_by_province = df_filtered.groupby('province')

#pydeck map for the average rain by province
province_map = df_filtered.groupby('province')[['longitude', 'latitude','rain']].mean()

# Display the map
st.subheader("Map show rain in each area")

# Map show rain in each area
layer = pdk.Layer(
    "ScatterplotLayer",
    province_map,
    pickable=True,
    opacity=0.8,
    filled=True,
    radius_scale=2500,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position= ["longitude", "latitude"],
    get_radius = ["rain"] ,
    get_fill_color=[108, 206, 245]
)

if df_filtered.empty:
    view_state = pdk.ViewState(
        longitude=df['longitude'].mean(),
        latitude=df['latitude'].mean(),
        zoom=4.5,
    )
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state= view_state,
    )
    st.pydeck_chart(r)
else:
    view_state = pdk.ViewState(
        longitude=province_map['longitude'].mean(),
        latitude=province_map['latitude'].mean(),
        zoom=4.5,
    )
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Rain: {rain} mm"},
    )
    st.pydeck_chart(r)

# Display summary 
st.subheader("Summary of Rainfall Analysis")

if df_filtered.empty:
    summary_text = "The analysis of the rainfall data shows that there is no data available for the selected provinces and dates."
    st.write(summary_text)
else: 
    highest_rain = avg_rain_by_province['rain'].mean().max()
    lowest_rain = avg_rain_by_province['rain'].mean().min()

    summary_text = f"The analysis of the rainfall data shows that the province with the highest average rainfall is {avg_rain_by_province['rain'].mean().idxmax()} with an average of {highest_rain:.2f} mm. The province with the lowest average rainfall is {avg_rain_by_province['rain'].mean().idxmin()} with an average of {lowest_rain:.2f} mm."
    st.write(summary_text)

# Display the source code
st.subheader("Source Code")
with open('app.py', "r", encoding="utf-8") as f:
    code = f.read()
st.code(code, language="python")