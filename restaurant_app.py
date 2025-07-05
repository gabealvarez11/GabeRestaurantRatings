import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Restaurant Finder", layout="wide")

# App title
st.title("🍽️ Restaurant Finder")
st.markdown("---")

# Sample restaurant data
restaurants_data = {
    'Name': [
        'The Golden Spoon',
        'Bella Vista Italian',
        'Sakura Sushi Bar',
        'Taco Libre',
        'The Coffee House'
    ],
    'Cuisine': [
        'American Fine Dining',
        'Italian',
        'Japanese',
        'Mexican',
        'Cafe'
    ],
    'Rating': [4.5, 4.2, 4.7, 4.1, 4.3],
    'Price Range': ['$$$', '$$', '$$$', '$', '$$'],
    'Address': [
        '123 Main St, Downtown',
        '456 Oak Ave, Little Italy',
        '789 Pine Rd, Midtown',
        '321 Elm St, Arts District',
        '654 Maple Dr, University Area'
    ],
    'Phone': [
        '(555) 123-4567',
        '(555) 234-5678',
        '(555) 345-6789',
        '(555) 456-7890',
        '(555) 567-8901'
    ],
    'Hours': [
        '5:00 PM - 10:00 PM',
        '11:00 AM - 9:00 PM',
        '12:00 PM - 10:00 PM',
        '11:00 AM - 8:00 PM',
        '7:00 AM - 6:00 PM'
    ]
}

# Create DataFrame
df = pd.DataFrame(restaurants_data)

# Add coordinates for map (sample coordinates around a city center)
# In a real app, you'd use geocoding to get actual coordinates
np.random.seed(42)  # For consistent coordinates
base_lat, base_lon = 37.7749, -122.4194  # SF coordinates as example
df['latitude'] = base_lat + np.random.uniform(-0.01, 0.01, len(df))
df['longitude'] = base_lon + np.random.uniform(-0.01, 0.01, len(df))

# Sidebar filters
st.sidebar.header("🔍 Filter Restaurants")

# Cuisine filter
cuisine_options = ['All'] + list(df['Cuisine'].unique())
selected_cuisine = st.sidebar.selectbox("Select Cuisine:", cuisine_options)

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating:", 1.0, 5.0, 1.0, 0.1)

# Price range filter
price_options = ['All'] + list(df['Price Range'].unique())
selected_price = st.sidebar.selectbox("Price Range:", price_options)

# Apply filters
filtered_df = df.copy()

if selected_cuisine != 'All':
    filtered_df = filtered_df[filtered_df['Cuisine'] == selected_cuisine]

filtered_df = filtered_df[filtered_df['Rating'] >= min_rating]

if selected_price != 'All':
    filtered_df = filtered_df[filtered_df['Price Range'] == selected_price]

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📋 Restaurant List")
    
    if len(filtered_df) > 0:
        # Display table without lat/lon columns
        display_df = filtered_df.drop(['latitude', 'longitude'], axis=1)
        
        # Style the dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("Restaurant Name", width="medium"),
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "Price Range": st.column_config.TextColumn("Price", width="small"),
                "Phone": st.column_config.TextColumn("Phone", width="medium"),
                "Hours": st.column_config.TextColumn("Hours", width="medium")
            }
        )
        
        # Summary statistics
        st.markdown("### 📊 Summary")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Restaurants", len(filtered_df))
        with col_b:
            st.metric("Average Rating", f"{filtered_df['Rating'].mean():.1f}⭐")
        with col_c:
            st.metric("Top Rated", f"{filtered_df['Rating'].max():.1f}⭐")
    else:
        st.warning("No restaurants match your filters. Try adjusting your criteria.")

with col2:
    st.subheader("🗺️ Restaurant Locations")
    
    if len(filtered_df) > 0:
        # Create interactive map with Plotly
        fig = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            hover_name="Name",
            hover_data={
                "Cuisine": True,
                "Rating": True,
                "Price Range": True,
                "Address": True,
                "Phone": True,
                "Hours": True,
                "latitude": False,
                "longitude": False
            },
            color="Rating",
            size="Rating",
            color_continuous_scale="Viridis",
            size_max=20,
            zoom=12,
            height=500
        )
        
        # Update map layout
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_colorbar=dict(
                title="Rating",
                title_side="right"
            )
        )
        
        # Customize hover template
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>" +
                         "🍽️ Cuisine: %{customdata[0]}<br>" +
                         "⭐ Rating: %{customdata[1]}<br>" +
                         "💰 Price: %{customdata[2]}<br>" +
                         "📍 Address: %{customdata[3]}<br>" +
                         "📞 Phone: %{customdata[4]}<br>" +
                         "🕐 Hours: %{customdata[5]}<br>" +
                         "<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Instructions for map interaction
        st.info("💡 **Tip:** Hover over or click on the markers to see restaurant details!")
        
        # Optional: Show summary of filtered restaurants
        st.markdown("### 📋 Filtered Restaurants")
        for _, restaurant in filtered_df.iterrows():
            with st.expander(f"🍽️ {restaurant['Name']} - {restaurant['Rating']}⭐"):
                st.markdown(f"""
                **{restaurant['Name']}**
                
                🍽️ **Cuisine:** {restaurant['Cuisine']}  
                ⭐ **Rating:** {restaurant['Rating']}  
                💰 **Price:** {restaurant['Price Range']}  
                📍 **Address:** {restaurant['Address']}  
                📞 **Phone:** {restaurant['Phone']}  
                🕐 **Hours:** {restaurant['Hours']}
                """)
    else:
        st.info("No restaurants to display on map.")

# Footer
st.markdown("---")
st.markdown("*This is a sample restaurant finder app. In a real application, you would connect to actual restaurant data and use geocoding services for precise locations.*")