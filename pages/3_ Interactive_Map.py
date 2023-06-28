import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import pandas as pd


APP_TITLE = 'CRIME STATS INTERACTIVE MAP 🗺️ '

@st.cache_data
def load_data():
    Top3_CrimeStats = gpd.read_file('data/Top3_SouthA_CrimeStats_withProb_gdf_top3.shp')
    Crime_Grading = gpd.read_file('data/SouthA_CrimeStats_withGeo_overall_Prop_merge_gdf.shp')
    Prov_Bounds = gpd.read_file('data/ZAF_adm1.shp')
    City_bounds = gpd.read_file('data/ZAF_adm2.shp')
    Crime_Rate_of_change = pd.read_csv('data/Crime_dtata.csv')
    Crime_Grading = Crime_Grading.merge(Crime_Rate_of_change[['Station', 'Category', 'Yearly Average']], on=['Station', 'Category'], how='left', suffixes=('', '_y'))

    return Top3_CrimeStats, Prov_Bounds, City_bounds, Crime_Grading, Crime_Rate_of_change


def add_crime_markers(m, crime_df, station_col, crimes_col, bin_col, yearly_avg_col, probability_col, lat='latitude', lon='longitude'):
    for index, row in crime_df.iterrows():
        station_name = row[station_col]
        crimes = row[crimes_col]
        bins = row[bin_col]
        yearly_avg = row[yearly_avg_col]  # Added 'Yearly Average' column
        probability = row[probability_col]  # Added 'Probability' column

        color_dict = 'green' if bins == 'Low' else ('yellow' if bins == 'Medium' else ('orange' if bins == 'High' else 'red'))

        lat = row.geometry.centroid.y
        lon = row.geometry.centroid.x

        max_width = 200
        popup_content = f'<div style="max-width: {max_width}px;">'
        popup_content += f'<b>{station_col}:</b> {station_name}<br>'
        popup_content += f'<b>{crimes_col}:</b> {crimes}<br>'
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
    st.sidebar.write("Date source: https://www.saps.gov.za/.")

def main():
    st.set_page_config( page_icon="🗺️",layout="wide", page_title=APP_TITLE)
    st.title(APP_TITLE)

    # LOAD DATA
    Top3_CrimeStats, Prov_Bounds, City_bounds, Crime_Grading, Crime_Rate_of_change = load_data()

    # View the dataframe
    #st.write(Crime_Grading)

    # Sidebar for select boxes
    with st.sidebar:
        # Select province
        province_options = Crime_Grading['Province'].unique().tolist()
        selected_province = st.selectbox('Select Province', province_options)

        # Filter stations based on selected province
        if selected_province != 'All':
            filtered_stations = Crime_Grading[Crime_Grading['Province'] == selected_province]
        else:
            filtered_stations = Crime_Grading  # Display all stations

        # Select station
        station_options = ['All'] + filtered_stations['Station'].unique().tolist()
        selected_station = st.selectbox('Select Station', station_options)

        if selected_station != 'All':
            # Filter Crime based on selected station
            filtered_crime = Crime_Grading[Crime_Grading['Station'] == selected_station]
        else:
            filtered_crime = filtered_stations  # Display all crime data

        # Select crime
        crime_options = ['All'] + filtered_crime['Category'].unique().tolist()
        selected_crime = st.selectbox('Select Crime', crime_options)

        if selected_crime != 'All':
            # Filter Crime based on selected crime
            filtered_crime = filtered_crime[filtered_crime['Category'] == selected_crime]

        # Select bin size
        bin_sizes = ['All'] + filtered_crime['Bins'].unique().tolist()
        selected_bin_size = st.selectbox('Select Bin Size', bin_sizes)

        if selected_bin_size != 'All':
            # Filter Crime based on selected bin size
            filtered_crime = filtered_crime[filtered_crime['Bins'] == selected_bin_size]

    # Display crime information for the selected station
    selected_station_data = filtered_stations[filtered_stations['Station'] == selected_station]
    if not selected_station_data.empty:
        st.write('Filtered Crime Information:')
        st.write(filtered_crime)

    # Convert Prov_Bounds and City_bounds to GeoJSON
    Prov_Bounds_geojson = Prov_Bounds.to_json()
    City_bounds_geojson = City_bounds.to_json()

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
    folium.GeoJson(City_bounds_geojson, name='City Bounds').add_to(m)
    folium.GeoJson(Prov_Bounds_geojson, name='Province Bounds', style_function=lambda x: {'color': 'black'}).add_to(m)

    folium.plugins.Geocoder().add_to(m)
    folium.TileLayer('OpenStreetMap', control=True).add_to(m)
    #folium.LayerControl().add_to(m)

    # Add crime markers
     # Add crime markers
    probability_col = 'Probabilit'  # Specify the column name for 'Probability'
    yearly_avg_col = 'Yearly Average'  # Specify the column name for 'Yearly Average'
    if selected_province != 'All':
        add_crime_markers(m, filtered_crime, 'Station', 'Category', 'Bins', yearly_avg_col, probability_col, lat ='latitude', lon ='longitude')
    else:
        add_crime_markers(m, Crime_Grading, 'Station', 'Category', 'Bins', yearly_avg_col, probability_col, lat ='latitude', lon ='longitude')

   # Sidebar for select boxes
    with st.sidebar:
        show_sidebar_content()

    st_folium(m)

    # Button to manually trigger re-execution
    if st.button("Rerun"):
        st.stop()

    # Save the map as an HTML file
    m.save("crime_map.html")


if __name__ == "__main__":
    main()
