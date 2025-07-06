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
    st.markdown("We've tried over 200 spots around town and have identified the following restaurants as deserving of one, two, or three 'Caro-lin' stars.")
    st.markdown("Use the filters on the left to narrow the options, then select a restaurant on the map or in the list to see more details, including our review.")

def get_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
    df[["latitude", "longitude"]] = df.pop("lat_long").str.split(",", expand=True).astype(float)
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
    fig = px.scatter_map(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="Name",
        hover_data={
            "Cuisine": True,
            "Rating": True,
            "Price Range": True,
            "Address": True,
            "Website": True,
            "Blurb":False,
            "latitude": False,
            "longitude": False,
        },
        zoom=12,
        height=500
    )
    
    # Update map layout with clean light theme
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
    )
    
    # Customize hover template with better styling
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                    "🍽️ Cuisine: %{customdata[0]}<br>" +
                    "⭐ Rating: %{customdata[1]}<br>" +
                    "💰 Price: %{customdata[2]}<br>" +
                    "📍 Address: %{customdata[3]}<br>" +
                    "🌐 Website: See table." +
                    "<extra></extra>",
        marker=dict(size=20, opacity=0.9)
    )

    selected_points = st.plotly_chart(
        fig, 
        use_container_width=True, 
        key="restaurant_map",
        on_select="rerun",
        selection_mode="points"
    )

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # Handle click events
    if selected_points and selected_points.selection and selected_points.selection.points:
        clicked_point = selected_points.selection.points[0]
        point_index = clicked_point['point_index']
        clicked_restaurant = filtered_df.iloc[point_index]['Name']
        st.session_state.selected_restaurant = clicked_restaurant
        st.info("💡 **Tip:** Double-click anywhere on the map to unselect.")
    else:
        # User clicked on empty area (no points selected)
        # Reset the selection
        st.session_state.selected_restaurant = None
        st.session_state.show_popup = False

def make_table(fitered_df):
    # Display table with clickable rows
    st.dataframe(
        filtered_df.drop(columns=["latitude", "longitude", "Blurb"]).copy(),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Restaurant Name", width="medium"),
            "Rating": st.column_config.TextColumn("Rating", width = "small"),
            "Price Range": st.column_config.TextColumn("Price", width="small"),
            "Website": st.column_config.LinkColumn("Website", width="medium"),
        },
        on_select="rerun",
        selection_mode="single-row",
        key="restaurant_table"
    )
    
    # Handle table selection
    if st.session_state.get("restaurant_table", {}).get("selection", {}).get("rows"):
        selected_row = st.session_state.restaurant_table.selection.rows[0]
        selected_restaurant_name = filtered_df.iloc[selected_row]['Name']
        st.session_state.selected_restaurant = selected_restaurant_name

def show_selected_restaurant(filtered_df):
    selected_info = filtered_df[filtered_df['Name'] == st.session_state.selected_restaurant].iloc[0]
            
    st.subheader("🏷️ Selected Restaurant")

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
    st.subheader("📋 Restaurant List")
    
    if len(filtered_df) > 0:
        make_table(filtered_df)
        
        # Display selected restaurant information
        if st.session_state.selected_restaurant and st.session_state.selected_restaurant in filtered_df['Name'].values:
            show_selected_restaurant(filtered_df)
        else:
            st.markdown("### 🏷️ Restaurant Details")
            st.info("💡 **Tip:** Click on a marker or restaurant in the table to see detailed information!")
    else:
        st.warning("No restaurants match your filters. Try adjusting your criteria.")

# Footer
st.markdown("---")
st.markdown("*Please check back for more upcoming reviews, or reach out if you have any recommendations!*")