import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium


def show_sidebar_content():
    # Sidebar content
    st.sidebar.subheader("About")
    st.sidebar.write(
        "This Streamlit app presents crime statistics on an interactive map."
    )
    st.sidebar.write("Data source: https://www.saps.gov.za/.")


def main():
    # Main function to run the Streamlit app
    st.set_page_config(page_icon="🏠", layout="wide", page_title="SafeGuard Pro")

    # Introduction for the homepage
    st.markdown(
        """
        <div style='text-align: center;'>
            <h2 style='font-size: 50px; font-weight: bold;'>Welcome to SafeGuard Pro 🗺️</h2>
            <h3>Your interactive guide to understanding regional safety!</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar content
    with st.sidebar:
        show_sidebar_content()

    st.markdown(
        """
        <div style='text-align: center;'>
            <h2>What Helped Build the Model</h2>
            <p>Delve into the core of our robust model! We've harnessed the power of credible and comprehensive data sources to illuminate the intricate landscape of crime types in South Africa.
            Our approach not only highlights the prevalent crime categories but also paves the way for a deeper, data-driven exploration into the underlying patterns and trends.
            This insightful journey into data analysis is your window to understanding and effectively responding to the dynamic crime scenario.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # st.markdown(
    #     """
    #   <div style='text-align: center;'>
    #         <p>In this section, we present an analysis of crime statistics within South Africa.</p>
    #         <p>The data has been gathered from reliable sources and visualized to offer insights into the different crime grades.</p>
    #     </div>
    # """,
    #     unsafe_allow_html=True,
    # )

    # Load the data
    Crime_Grading = gpd.read_file("data/SouthAfrican_CrimeStats_withGeo_V4.shp")
    Prov_Bounds = gpd.read_file("data/ZAF_adm1.shp")
    Fire_Station = gpd.read_file("data/Fire_Station_V2.shp")

    # Convert geometry column to string representation
    Crime_Grading["geometry"] = Crime_Grading["geometry"].astype(str)

    # View the dataframes
    # st.subheader("Crime Grading and Stats")
    st.markdown(
        '<div style="text-align: center;"><h3>Crime Grading and Stats</h3></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(Crime_Grading.head())

    # Convert geometry column to string representation
    Prov_Bounds["geometry"] = Prov_Bounds["geometry"].astype(str)
    # View the dataframes
    # st.subheader("Administrative Boundaries")
    st.markdown(
        '<div style="text-align: center;"><h3>Administrative Boundaries</h3></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(Prov_Bounds.head())


if __name__ == "__main__":
    main()
