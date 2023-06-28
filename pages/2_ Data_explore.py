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
   

    Crime_Grading = gpd.read_file('data/SouthA_CrimeStats_withGeo_overall_Prop_merge_gdf.shp')
    Prov_Bounds = gpd.read_file('data/ZAF_adm1.shp')
    City_bounds = gpd.read_file('data/ZAF_adm2.shp')
    Crime_Rate_of_change = pd.read_csv('data/Crime_dtata.csv')

    # View the dataframes
    st.subheader("Crime_Grading")
    st.write(Crime_Grading.head())
    st.subheader("Crime_Rate_of_change")
    st.write(Crime_Rate_of_change.head())    

if __name__ == "__main__":
    main()
