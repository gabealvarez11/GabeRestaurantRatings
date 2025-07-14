import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

def setup_page():
    # Set page configuration
    st.set_page_config(page_title="Bay Area Veggie", layout="wide")

    # App title
    st.title("🍽️ Bay Area vegetarian eats, curated by Gabe and Carol")
    st.markdown("---")
    st.markdown("We've tried over 200 spots around town and have identified the following restaurants as deserving of one, two, or three 'Caro-lin' [stars](https://en.wikipedia.org/wiki/Michelin_Guide#Stars):")
    st.markdown(" - ⭐: A very good restaurant in its category")
    st.markdown(" - ⭐⭐: Excellent cooking, worth a detour")
    st.markdown(" - ⭐⭐⭐: Exceptional cuisine, worth a special journey")
    st.markdown("Use the filters on the left to narrow the options, then select a restaurant on the map to see more details, including our review. Or just scroll through all relevant restaurants!")

def get_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
    df[["lat", "lon"]] = df.pop("lat_long").str.split(",", expand=True).astype(float)
    return df

def filter_data(df):
    # Sidebar filters
    st.sidebar.header("🔍 Filter Restaurants")

    # Cuisine filter
    cuisine_options = ['All'] + list(df['Cuisine'].unique())
    selected_cuisine = st.sidebar.selectbox("Select Cuisine:", cuisine_options)

    # Rating filter
    min_rating = st.sidebar.slider("Minimum Rating (⭐):", 1, 3, 1, 1)

    # Price range filter
    price_options = ['All'] + list(df['Price Range'].unique())
    selected_price = st.sidebar.selectbox("Price Range:", price_options)

    # Apply filters
    filtered_df = df.copy()

    if selected_cuisine != 'All':
        filtered_df = filtered_df[filtered_df['Cuisine'] == selected_cuisine]

    filtered_df = filtered_df[filtered_df['Rating'] >= min_rating]

    def format_stars(rating):
        return "⭐" * int(rating) if rating > 0 else ""

    filtered_df["Rating"] = filtered_df["Rating"].apply(format_stars)

    if selected_price != 'All':
        filtered_df = filtered_df[filtered_df['Price Range'] == selected_price]

    return filtered_df

def make_map(filtered_df):
    # Create interactive map with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['lon'],
        mode='markers',
        hovertext=filtered_df["Name"],
        customdata = filtered_df[["Cuisine","Rating"]].values
    ))
    
    # Update map layout with clean light theme
    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=df['lat'].mean(), lon=df['lon'].mean()),
            zoom=8
        ), 
        height=500,
        dragmode="pan",       
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    # Customize hover template with better styling
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                    "Cuisine: %{customdata[0]}<br>" +
                    "Rating: %{customdata[1]}<br>" +
                    "<extra></extra>",
        marker=dict(size=20, opacity=0.9)
    )

    # selected_points = st.plotly_chart(
    #     fig, 
    #     use_container_width=True, 
    #     key="restaurant_map",
    #     on_select="rerun",
    #     selection_mode="points"
    # )

    selected_points = st.plotly_chart(
        fig,
        on_select="rerun",
        key="map_selection",
        config={"scrollZoom": True}
    )

    # Check for any event data
    # st.write("All session state:", {k: v for k, v in st.session_state.items() if 'map' in k})
    #st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # Handle click events
    if selected_points and selected_points.selection and selected_points.selection.points:
        clicked_point = selected_points.selection.points[0]
        point_index = clicked_point['point_index']
        clicked_restaurant = filtered_df.iloc[point_index]['Name']
        st.session_state.selected_restaurant = clicked_restaurant
    else:
        # User clicked on empty area (no points selected)
        # Reset the selection
        st.session_state.selected_restaurant = None

def show_selected_restaurant(filtered_df, selected_restaurant):
    selected_info = filtered_df[filtered_df['Name'] == selected_restaurant].iloc[0]
    
    with st.container(border=True):
        st.markdown(f"### {selected_info['Name']}")
        st.write(f"🍽️ **Cuisine:** {selected_info['Cuisine']}")
        st.write(f"⭐ **Rating:** {selected_info['Rating']}")
        st.write(f"💰 **Price Range:** {selected_info['Price Range']}")
        st.write(f"📍 **Address:** {selected_info['Address']}")
        st.write(f"🌐 **Website:** {selected_info['Website']}")
        st.write(f"💬 **Blurb:** {selected_info['Blurb']}")

setup_page()
df = get_data()
filtered_df = filter_data(df)

# Main content area
col1, col2 = st.columns([1,1])

# Initialize selected restaurant in session state
if "selected_restaurant" not in st.session_state:
    st.session_state.selected_restaurant = None

with col1:
    st.subheader("🗺️ Restaurant Locations")

    if len(filtered_df) > 0:
        make_map(filtered_df)
    else:
        st.info("No restaurants to display on map.")

with col2:
    
    if len(filtered_df) > 0:

        # Display selected restaurant information
        if st.session_state.selected_restaurant and st.session_state.selected_restaurant in filtered_df['Name'].values:
            st.info("💡 **Tip:** To unselect, click the same marker again, click another resaurant's marker, or double-click anywhere else on the map.")
            st.subheader("📋 Restaurant Details")

            show_selected_restaurant(filtered_df, st.session_state.selected_restaurant)
        else:
            st.info("💡 **Tip:** Currently showing info for all restaurants in filter. Click on a restaurant in the map to see detailed information for just that one!")
            st.subheader("📋 Restaurant Details")

            for restaurant in filtered_df["Name"].unique():
                show_selected_restaurant(filtered_df, restaurant)

    else:
        st.warning("No restaurants match your filters. Try adjusting your criteria.")

# Footer
st.markdown("---")
st.markdown("*Please check back for more upcoming reviews, or reach out if you have any recommendations!*")