import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import pydeck as pdk

df = pd.read_csv('RainDaily_Tabular.csv')
df['date'] = pd.to_datetime(df['date'])
# Sidebar
st.sidebar.header('Sidebar Controls')
province = st.sidebar.selectbox('Select Province', df['province'].unique())
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

# Convert start_date and end_date to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on sidebar selections
filtered_df = df[(df['province'] == province) & (df['date'] >= start_date) & (df['date'] <= end_date)]

#Average of rain by province
st.subheader("Average of rain by province")
pmean = df.groupby('province')['rain'].mean()
fig = px.bar(pmean, y = "rain")
# Update layout
fig.update_layout(
    xaxis_title="Province",
    yaxis_title="Average of rain",
)
st.plotly_chart(fig)
#Average of rain by day
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')
if filtered_df.empty:
    st.subheader("Average of rain by day")
    dmean = df.groupby('date')['rain'].mean().reset_index()
    fig1 = px.line(dmean, x='date', y="rain")
    fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Average of rain",
    )
    st.plotly_chart(fig1)
else :
    st.subheader("Average of rain by day between " + start_date_str + " and " + end_date_str + " in " + province)
    dmean = filtered_df.groupby('date')['rain'].mean().reset_index()
    fig1 = px.line(dmean, x='date', y="rain")
    fig1.update_layout(
        xaxis_title="Date",
        yaxis_title="Average of rain",
    )
    st.plotly_chart(fig1)

province_centers = df.groupby('province')[['longitude', 'latitude','rain']].mean()
# Map show rain in each area
layer = pdk.Layer(
    "ScatterplotLayer",
    province_centers,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=2500,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position= ["longitude", "latitude"],
    get_radius = ["rain"] ,
    get_fill_color=[255, 140, 0],
    get_line_color=[255, 0, 0],
)
view_state = pdk.ViewState(
    longitude=province_centers['longitude'].mean(),
    latitude=province_centers['latitude'].mean(),
    zoom=9,
)
st.subheader("Map show rain in each area")
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "Rain: {rain} mm"},
)
st.pydeck_chart(r)

# Summary text
summary_text = "การวิเคราะห์ปริมาณน้ำฝนในเชิงพื้นที่และเวลาสามารถทำได้โดยการใช้ข้อมูลปริมาณน้ำฝนจากสถานีต่าง ๆ พบว่า ปริมาณน้ำฝนที่มากที่สุดคือ ในจังหวัดระนอง และปริมาณน้ำฝนที่น้อยที่สุดคือ ในจังหวัดพัทลุง"
# Display summary text
st.subheader("Summary of Rainfall Analysis")
st.text(summary_text)

st.subheader("Source Code")
with open('streamlit_ass.py', "r", encoding="utf-8") as f:
    code = f.read()
st.code(code, language="python")

