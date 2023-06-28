import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium


def show_sidebar_content():
    # About section
    st.sidebar.subheader("About")
    st.sidebar.write("This Streamlit app presents crime statistics on an interactive map.")
    st.sidebar.write("Date source: https://www.saps.gov.za/.") 

def main():
    
    st.set_page_config(page_icon="🏠", layout="wide")

    st.header("Welcome to the Crime Investigation App")
    st.markdown("This app allows you to investigate local crime data and visualize it on a map.")
    st.subheader("Instructions:")
    st.markdown("1. Use the sidebar to select filters for the crime data.")
    st.markdown("2. The filtered crime information will be displayed below the sidebar.")
    st.markdown("3. The map will show crime markers based on the selected filters.")
    st.markdown("4. You can interact with the map to explore the crime locations.")
    st.subheader("Crime Data Filters:")
    st.markdown("Use the options below to filter the crime data:")
    st.markdown("1. Filter for the province")
    st.markdown("2. Filter for the Police Station")
    st.markdown("3. Filter for the type of crime")
    st.markdown("4. Filter for the servity of the crime")

  # Sidebar for select boxes
    with st.sidebar:
        show_sidebar_content()
 
if __name__ == "__main__":
    main()
