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
    st.set_page_config(page_icon="🗄️", layout="wide")

 # Sidebar for select boxes
    with st.sidebar:
        show_sidebar_content()

    st.title("This is the dataframe explore page")
    st.header("what helped build the model")

    # Inserting a paragraph here
    st.write("""
    In this section, we present an analysis of crime statistics within South Africa. 
    The data has been gathered from reliable sources and visualized to offer insights 
    into the different crime grades. Further analysis can help in understanding the trends 
    and possibly in developing effective a risk mearsure.
    """)   

    Crime_Grading = gpd.read_file('data/SouthAfrican_CrimeStats_withGeo_V4.shp')
    Prov_Bounds = gpd.read_file('data/ZAF_adm1.shp')

    # View the dataframes
    st.subheader("Crime_Grading and stats")
    st.write(Crime_Grading.head())
    #st.subheader("Crime_Rate_of_change")
    #st.write(Crime_Rate_of_change.head())    

if __name__ == "__main__":
    main()
