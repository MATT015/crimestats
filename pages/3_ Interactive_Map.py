import streamlit as st
import folium
import geopandas as gpd
import pandas as pd
from streamlit_folium import folium_static

APP_TITLE = "SafeGuard Pro 🗺"

st.set_page_config(page_icon="🗺️", layout="wide", page_title=APP_TITLE)
# st.title(APP_TITLE)
# Center the app title using HTML and CSS
st.markdown(
    f"<h1 style='text-align: center;'>{APP_TITLE}</h1>",
    unsafe_allow_html=True,
)

# Your Mapbox Access Token
mapbox_access_token = "pk.eyJ1IjoibWF0dGJveHgtNTEiLCJhIjoiY2xwZ3d3bXVzMDFyeTJxdDN1bThxOWJsYSJ9.H0Ac62dg5ygowbqjtLiX8A"

# Mapbox Streets v12 tile URL
mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_access_token}"


@st.cache_data
def load_data():
    Top3_CrimeStats = gpd.read_file("data/Top3_SouthA_CrimeStats_withProb_gdf_top3.shp")
    merged_df = gpd.read_file("data/SouthAfrican_CrimeStats_withGeo_V4.shp")
    Prov_Bounds = gpd.read_file("data/ZAF_adm1.shp")
    City_bounds = gpd.read_file("data/ZAF_adm2.shp")
    Fire_Station = gpd.read_file("data/Fire_Station_V2.shp")
    Crime_Rate_of_change = pd.read_csv("data/Crime_Statsfinal_V2.csv")
    merged_df = merged_df.rename(
        columns={
            "City": "Station",
            "Crime cate": "Category",
            "average ye": "Yearly Average",
        }
    )
    # Create a mapping of police stations to provinces
    station_to_province = merged_df.set_index("Station")["Province"].to_dict()

    return (
        Top3_CrimeStats,
        Prov_Bounds,
        City_bounds,
        merged_df,
        Crime_Rate_of_change,
        Fire_Station,
        station_to_province,
    )


def add_crime_markers(
    m,
    crime_df,
    selected_province,
    station_col,
    crimes_col,
    bin_col,
    yearly_avg_col,
    probability_col,
    lat="latitude",
    lon="longitude",
):
    # Filter for the selected province
    if selected_province != "All":
        crime_df = crime_df[crime_df["Province"] == selected_province]
    for index, row in crime_df.iterrows():
        station_name = row[station_col]
        crimes = row[crimes_col]
        bins = row[bin_col]
        yearly_avg = row.get(
            yearly_avg_col
        )  # Get the value or None if column doesn't exist
        probability = row[probability_col]  # Added 'Probability' column

        color_dict = (
            "green"
            if bins == "Low"
            else (
                "yellow"
                if bins == "Medium"
                else ("orange" if bins == "High" else "red")
            )
        )

        lat = row.geometry.centroid.y
        lon = row.geometry.centroid.x

        # Set both min and max width for the popup box
        min_width = 200  # This ensures the popup has a minimum width
        max_width = 250  # Increase this value as needed for a wider popup box
        popup_content = (
            f'<div style="min-width: {min_width}px; max-width: {max_width}px;">'
        )
        popup_content += f"<b>Police Station:</b> {station_name}<br>"
        popup_content += f"<b>Crime Category:</b> {crimes}<br>"
        if yearly_avg is not None:
            popup_content += f"<b>10 year % change:</b> {round(yearly_avg, 2)}<br>"
        popup_content += f"<b>Highest Probability of crime %:</b> {round(probability, 2)}<br>"  # Include the probability
        popup_content += "<br>"
        popup_content += "Additional Information:"
        popup_content += "<br>"
        popup_content += "</div>"

        folium.CircleMarker(
            location=[lat, lon],
            popup=popup_content,
            radius=0.6,
            color=color_dict,
            fill=True,
            fill_color=color_dict,
            fill_opacity=0.6,
        ).add_to(m)


def show_sidebar_content():
     # Add margin before the about section
    st.sidebar.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    # About section
    st.sidebar.subheader("About")
    st.sidebar.write(
        "This Streamlit app presents crime statistics on an interactive map."
    )
    st.sidebar.write("Data source: https://www.saps.gov.za/.")


def crime_severity_legend():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Crime Severity Categorical Legend")

    # Define the legend data with color codes
    legend_data = {
        "Color": [
            "#008000",
            "#FFFF00",
            "#FFA500",
            "#FF0000",
        ],  # Green, Yellow, Orange, Red
        "Severity": ["Low", "Medium", "High", "Very High"],
    }
    legend_table = pd.DataFrame(legend_data)

    # Create a custom HTML table for the legend with enhanced styling
    legend_html = "<table style='border-collapse: collapse;'>"
    for i, row in legend_table.iterrows():
        color = row["Color"]
        severity = row["Severity"]
        legend_html += f"<tr>"
        legend_html += f"<td style='background-color:{color}; width: 20px; border: 1px solid #ddd;'>&nbsp;</td>"
        legend_html += f"<td style='padding-left: 10px; font-weight: bold; font-size: 14px;'>{severity}</td>"
        legend_html += f"</tr>"
    legend_html += "</table>"

    st.sidebar.markdown(legend_html, unsafe_allow_html=True)


def get_bounds_for_selection(province, station, merged_df, Prov_Bounds):
    """Calculate the bounds for the selected province or station."""
    if station and station != "All":
        # For a specific station, calculate more focused bounds
        station_data = merged_df[merged_df["Station"] == station]
        if not station_data.empty:
            bounds = station_data.geometry.total_bounds
            # Optionally, you can adjust the bounds here to zoom in even closer
            # For example, you can reduce the bounds by a certain percentage to zoom in more
    elif province and province != "All":
        # For a specific province, return the bounds of that province
        bounds = Prov_Bounds[Prov_Bounds["NAME_1"] == province].geometry.total_bounds
    else:
        # For "All" selection, return the bounds of the entire dataset
        bounds = merged_df.geometry.total_bounds
    return bounds


def get_province_bounds(province, Prov_Bounds):
    """Get the bounding box for the selected province."""
    if province in Prov_Bounds["NAME_1"].values:
        return Prov_Bounds[Prov_Bounds["NAME_1"] == province].total_bounds
    return None


def show_sidebar_guide():
    # Sidebar Guide or Instructions with Red Text
    st.sidebar.title("Guide")
    st.sidebar.markdown(
        """
        <style>
        .how-to-guide-text {
   
        }
        </style>
        <div class="how-to-guide-text">
            Welcome to the SafeGuard Pro Interactive Map!<br>
            Follow these steps to explore the data:<br>
            1. Select a Province from the dropdown.<br>
            2. Choose a Police Station, if desired.<br>
            3. Pick a Crime Category to filter the data.<br>
            4. Select Crime Severity to refine your search.<br>
            <strong>5. Click on the coloured circles with your cursor to see the highest crime probability for crimes reported in that police station.</strong><br>
            <br>
            The map will update automatically based on your selections.<br>
            Zoom in/out or drag the map to explore different areas.
        
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Add two-line space
    st.sidebar.markdown("<br>", unsafe_allow_html=True)


def get_bounds_for_selection(station, merged_df):
    """Calculate the bounds for the selected police station."""
    if station and station != "All":
        bounds = merged_df[merged_df["Station"] == station].geometry.total_bounds
        return bounds, True  # True indicates a specific station is selected
    else:
        # Return default bounds for a general view
        return merged_df.geometry.total_bounds, False


def main():

    # LOAD DATA
    (
        Top3_CrimeStats,
        Prov_Bounds,
        City_bounds,
        merged_df,
        Crime_Rate_of_change,
        Fire_Station,
        station_to_province,
    ) = load_data()

    # st.write(merged_df.head())
    # st.write(Crime_Rate_of_change.head())

    with st.sidebar:
        show_sidebar_guide()
    # Sidebar for select boxes
    with st.sidebar:
        # Initialize session states for province, station, and crime
        if "selected_province" not in st.session_state:
            st.session_state.selected_province = "All"
        if "selected_station" not in st.session_state:
            st.session_state.selected_station = "All"
        if "selected_crime" not in st.session_state:
            st.session_state.selected_crime = "All"

        # Province selection
        province_options = ["All"] + sorted(merged_df["Province"].unique().tolist())
        selected_province = st.selectbox(
            "Select Province",
            province_options,
            index=province_options.index(st.session_state.selected_province),
        )

        # Station selection
        if selected_province != "All":
            filtered_stations = merged_df[merged_df["Province"] == selected_province]
        else:
            filtered_stations = merged_df

        station_options = ["All"] + sorted(
            filtered_stations["Station"].unique().tolist()
        )
        selected_station = st.selectbox("Select Station", station_options)

        # Crime selection
        if selected_station != "All":
            filtered_crimes = merged_df[merged_df["Station"] == selected_station]
        else:
            filtered_crimes = filtered_stations

        crime_options = ["All"] + sorted(filtered_crimes["Category"].unique().tolist())
        selected_crime = st.selectbox("Select Crime", crime_options)

        # Severity selection
        severity_options = ["All"] + sorted(filtered_crimes["Bins"].unique().tolist())
        selected_severity = st.selectbox("Select Crime Severity", severity_options)

        # Filtering logic
        if selected_crime == "All" and selected_severity == "All":
            # Default to highest probability crimes
            filtered_crime = merged_df.sort_values(
                "Probabilit", ascending=False
            ).drop_duplicates("Station")
        else:
            filtered_crime = filtered_crimes
            if selected_crime != "All":
                filtered_crime = filtered_crime[
                    filtered_crime["Category"] == selected_crime
                ]
            if selected_severity != "All":
                filtered_crime = filtered_crime[
                    filtered_crime["Bins"] == selected_severity
                ]

        # # Additional warning when 'All' provinces are selected
        # if selected_province == "All":
        #     st.warning(
        #         "All crime category are shown randomly because all the select boxes are defaulted to 'All'.\n\nPLEASE NOTE THAT WARNING WILL DISAPPEAR WHEN YOU CHOOSE A PROVINCE",
        #         icon="⚠️",
        #     )

            # Initialize the map with a default view
        m = folium.Map(
            location=[-29.0, 24.0],  # Default coordinates for South Africa
            zoom_start=10,  # Default zoom level for a general view
            tiles=mapbox_url,
            attr="Map data © OpenStreetMap contributors, CC-BY-SA, Imagery © Mapbox",
        )

        # Calculate bounds and update map view
        bounds, is_station_selected = get_bounds_for_selection(
            selected_station, merged_df
        )

        if is_station_selected:
            # Update the map view for a specific station
            zoom_level = 13  # Closer zoom level for specific station
            m.fit_bounds(
                [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            )  # Apply the calculated bounds
            m.zoom_start = zoom_level

    # Add the GeoJSON layer to the map
    folium.GeoJson(
        City_bounds,
        name="City Bounds",
        style_function=lambda x: {"color": "blue", "weight": 2, "opacity": 1},
    ).add_to(m)
    folium.GeoJson(
        Prov_Bounds,
        name="Province Bounds",
        style_function=lambda x: {"color": "black", "weight": 2, "opacity": 1},
    ).add_to(m)

    # Add crime markers
    probability_col = "Probabilit"  # Specify the column name for 'Probability'
    yearly_avg_col = "Yearly Average"  # Specify the column name for 'Yearly Average'

    # Add crime markers
    add_crime_markers(
        m,
        filtered_crime,
        selected_province,  # pass the selected province
        "Station",
        "Category",
        "Bins",
        yearly_avg_col,
        probability_col,
        lat="latitude",
        lon="longitude",
    )

    # Sidebar for select boxes
    with st.sidebar:
        crime_severity_legend()
        show_sidebar_content()

    # Calculate bounds and update map view
    bounds, is_station_selected = get_bounds_for_selection(selected_station, merged_df)
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    folium_static(m, width=None, height=700)
    # full screen
    # folium_static(m, width=None, height=None)

    # Save the map as an HTML file
    m.save("crime_map.html")


if __name__ == "__main__":
    main()
