import streamlit as st
import folium
import geopandas as gpd
import pandas as pd
from streamlit_folium import folium_static

APP_TITLE = 'CRIME STATS INTERACTIVE MAP 🗺️ '

@st.cache_data
def load_data():
    Top3_CrimeStats = gpd.read_file('data/Top3_SouthA_CrimeStats_withProb_gdf_top3.shp')
    merged_df = gpd.read_file('data/SouthAfrican_CrimeStats_withGeo_V4.shp')
    Prov_Bounds = gpd.read_file('data/ZAF_adm1.shp')
    City_bounds = gpd.read_file('data/ZAF_adm2.shp')
    Fire_Station = gpd.read_file('data/Fire_Station_V2.shp')
    Crime_Rate_of_change = pd.read_csv('data/Crime_Statsfinal_V2.csv')
    merged_df = merged_df.rename(columns={'City': 'Station','Crime cate':'Category','average ye':'Yearly Average'})

    return Top3_CrimeStats, Prov_Bounds, City_bounds, merged_df, Crime_Rate_of_change,Fire_Station 

def add_crime_markers(m, crime_df, station_col, crimes_col, bin_col, yearly_avg_col, probability_col, lat='latitude', lon='longitude'):
    for index, row in crime_df.iterrows():
        station_name = row[station_col]
        crimes = row[crimes_col]
        bins = row[bin_col]
        yearly_avg = row.get(yearly_avg_col)  # Get the value or None if column doesn't exist
        probability = row[probability_col]  # Added 'Probability' column

        color_dict = 'green' if bins == 'Low' else ('yellow' if bins == 'Medium' else ('orange' if bins == 'High' else 'red'))

        lat = row.geometry.centroid.y
        lon = row.geometry.centroid.x

        max_width = 200
        popup_content = f'<div style="max-width: {max_width}px;">'
        popup_content += f'<b>{station_col}:</b> {station_name}<br>'
        popup_content += f'<b>{crimes_col}:</b> {crimes}<br>'
        if yearly_avg is not None:
            popup_content += f'<b>10 year % change:</b> {round(yearly_avg, 2)}<br>'
        popup_content += f'<b>Probability of crime:</b> {round(probability, 2)}<br>'  # Include the probability
        popup_content += '<br>'
        popup_content += 'Additional Information:'
        popup_content += '<br>'
        popup_content += '</div>'

        folium.CircleMarker(
            location=[lat, lon],
            popup=popup_content,
            radius=0.6,
            color=color_dict,
            fill=True,
            fill_color=color_dict,
            fill_opacity=0.6
        ).add_to(m)


def show_sidebar_content():
    # About section
    st.sidebar.subheader("About")
    st.sidebar.write("This Streamlit app presents crime statistics on an interactive map.")
    st.sidebar.write("Data source: https://www.saps.gov.za/.")


def crime_severity_legend():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Crime Severity Categorical Legend")
    legend_data = {
        'Color': ['Green', 'Yellow', 'Orange', 'Red'],
        'Severity': ['Low', 'Medium', 'High', 'Very High']
    }
    legend_table = pd.DataFrame(legend_data)
    st.sidebar.table(legend_table)


def main():
    st.set_page_config(page_icon="🗺️", layout="wide", page_title=APP_TITLE)
    st.title(APP_TITLE)

    # LOAD DATA
    Top3_CrimeStats, Prov_Bounds, City_bounds, merged_df, Crime_Rate_of_change,Fire_Station = load_data()

    #st.write(merged_df.head())
    #st.write(Crime_Rate_of_change.head())

    # Sidebar for select boxes
    with st.sidebar:
       # Select province
        province_options = ['All'] + merged_df['Province'].unique().tolist() # Include 'All' option
        selected_province = st.selectbox('Select Province', province_options)

        # Filter stations based on selected province
        if selected_province == 'All':
            filtered_stations = merged_df[merged_df['Bins'] == 'Very High'] # Only select "Very High" crimes
        else:
            filtered_stations = merged_df[merged_df['Province'] == selected_province]

        # Select station
        station_options = ['All'] + filtered_stations['Station'].unique().tolist()
        selected_station = st.selectbox('Select Station', station_options)

        if selected_station != 'All':
            # Filter Crime based on selected station
            filtered_crime = merged_df[merged_df['Station'] == selected_station]
        else:
            filtered_crime = filtered_stations  # Display all crime data

        # Select crime
        crime_options = ['All'] + filtered_crime['Category'].unique().tolist()
        selected_crime = st.selectbox('Select Crime', crime_options)

        if selected_crime != 'All':
            # Filter Crime based on selected crime
            filtered_crime = filtered_crime[filtered_crime['Category'] == selected_crime]
      
         # Select bin size
        if selected_province == 'All':
            st.warning("Only 'High and Very High' crimes are shown when selecting 'All' provinces.",icon="⚠️")

        bin_sizes = ['All'] + filtered_crime['Bins'].unique().tolist()
        selected_bin_size = st.selectbox('Select Crime Severity', bin_sizes)

        if selected_bin_size != 'All':
            # Filter Crime based on selected bin size
            filtered_crime = filtered_crime[filtered_crime['Bins'] == selected_bin_size]


    # Create the base map
    m = folium.Map(
        location=[-30.5595, 22.9375],
        zoom_start=6,
        control_scale=True,
        scrollWheelZoom=False,
        tiles='OpenStreetMap',
        width='100%',  # Adjust the map width
        height='100%',  # Adjust the map height
    )

    # Add the GeoJSON layer to the map
    folium.GeoJson(City_bounds, name='City Bounds').add_to(m)
    folium.GeoJson(Prov_Bounds, name='Province Bounds', style_function=lambda x: {'color': 'black'}).add_to(m)

    # # Iterate through Fire Station locations and add them to the map
    # for index, row in Fire_Station.iterrows():
    #     lat = row['lat']
    #     lon = row['lng']
    #     folium.Circle(
    #         location=[lat, lon],
    #         radius=500,  # Adjust the radius as needed
    #         color='white',
    #         fill=True,
    #         fill_color='white',
    #         fill_opacity=0.6
    #     ).add_to(m)

    # Add crime markers
    probability_col = 'Probabilit'  # Specify the column name for 'Probability'
    yearly_avg_col = 'Yearly Average'  # Specify the column name for 'Yearly Average'
    if selected_province != 'All':
        add_crime_markers(m, filtered_crime, 'Station', 'Category', 'Bins', yearly_avg_col, probability_col, lat='latitude', lon='longitude')
    else:
        add_crime_markers(m, merged_df, 'Station', 'Category', 'Bins', yearly_avg_col, probability_col, lat='latitude', lon='longitude')

    # Sidebar for select boxes
    with st.sidebar:
        crime_severity_legend()
        show_sidebar_content()

    folium_static(m)

    # Save the map as an HTML file
    m.save("crime_map.html")


if __name__ == "__main__":
    main()
