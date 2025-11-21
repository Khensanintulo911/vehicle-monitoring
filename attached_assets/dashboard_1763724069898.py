import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Fleet Management Dashboard", layout="wide")

API_BASE_URL = "http://0.0.0.0:5000/api"

@st.cache_data(ttl=30)
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

st.title("Fleet Management Analytics Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trips", "Performance", "Map View"])

with tab1:
    st.header("Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    trips_data = fetch_data("trips")
    jobs_data = fetch_data("jobs")
    drivers_data = fetch_data("drivers")
    vehicles_data = fetch_data("vehicles")
    
    with col1:
        st.metric("Total Trips", len(trips_data))
    
    with col2:
        active_trips = [t for t in trips_data if t['status'] == 'started']
        st.metric("Active Trips", len(active_trips))
    
    with col3:
        pending_jobs = [j for j in jobs_data if j['status'] == 'pending']
        st.metric("Pending Jobs", len(pending_jobs))
    
    with col4:
        active_drivers = [d for d in drivers_data if d['is_active']]
        st.metric("Active Drivers", len(active_drivers))
    
    if trips_data:
        df_trips = pd.DataFrame(trips_data)
        df_trips['start_time'] = pd.to_datetime(df_trips['start_time'])
        
        st.subheader("Recent Trips")
        recent_trips = df_trips.sort_values('start_time', ascending=False).head(10)
        
        display_cols = ['trip_number', 'driver_name', 'vehicle_name', 'start_time', 
                        'distance_travelled', 'duration_minutes', 'status']
        available_cols = [col for col in display_cols if col in recent_trips.columns]
        st.dataframe(recent_trips[available_cols], use_container_width=True)

with tab2:
    st.header("Trip Details")
    
    if trips_data:
        df_trips = pd.DataFrame(trips_data)
        df_trips['start_time'] = pd.to_datetime(df_trips['start_time'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            completed_trips = df_trips[df_trips['status'] == 'completed']
            if not completed_trips.empty and 'distance_travelled' in completed_trips.columns:
                completed_trips['distance_travelled'] = pd.to_numeric(
                    completed_trips['distance_travelled'], errors='coerce'
                )
                avg_distance = completed_trips['distance_travelled'].mean()
                st.metric("Average Distance per Trip", f"{avg_distance:.1f} km" if pd.notna(avg_distance) else "N/A")
        
        with col2:
            if not completed_trips.empty and 'duration_minutes' in completed_trips.columns:
                completed_trips['duration_minutes'] = pd.to_numeric(
                    completed_trips['duration_minutes'], errors='coerce'
                )
                avg_duration = completed_trips['duration_minutes'].mean()
                st.metric("Average Trip Duration", f"{avg_duration:.0f} min" if pd.notna(avg_duration) else "N/A")
        
        st.subheader("Trips Over Time")
        df_trips['date'] = df_trips['start_time'].dt.date
        trips_by_date = df_trips.groupby('date').size().reset_index(name='count')
        fig = px.line(trips_by_date, x='date', y='count', title='Daily Trip Count')
        st.plotly_chart(fig, use_container_width=True)
        
        if 'distance_travelled' in df_trips.columns:
            st.subheader("Distance Distribution")
            fig = px.histogram(completed_trips, x='distance_travelled', 
                             title='Trip Distance Distribution', nbins=20)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trip data available yet.")

with tab3:
    st.header("Driver Performance")
    
    if trips_data:
        df_trips = pd.DataFrame(trips_data)
        
        if 'driver_name' in df_trips.columns:
            driver_stats = df_trips.groupby('driver_name').agg({
                'trip_number': 'count',
                'distance_travelled': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'duration_minutes': lambda x: pd.to_numeric(x, errors='coerce').sum(),
                'fuel_consumed': lambda x: pd.to_numeric(x, errors='coerce').sum()
            }).reset_index()
            
            driver_stats.columns = ['Driver', 'Total Trips', 'Total Distance (km)', 
                                   'Total Duration (min)', 'Total Fuel (L)']
            
            st.subheader("Driver Statistics")
            st.dataframe(driver_stats, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(driver_stats, x='Driver', y='Total Trips', 
                           title='Trips per Driver')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(driver_stats, x='Driver', y='Total Distance (km)', 
                           title='Distance per Driver')
                st.plotly_chart(fig, use_container_width=True)
        
        completed = df_trips[df_trips['status'] == 'completed']
        if not completed.empty:
            st.subheader("Route Compliance")
            if 'route_compliance' in completed.columns:
                completed['route_compliance'] = pd.to_numeric(
                    completed['route_compliance'], errors='coerce'
                )
                avg_compliance = completed['route_compliance'].mean()
                st.metric("Average Route Compliance", 
                         f"{avg_compliance:.1f}%" if pd.notna(avg_compliance) else "N/A")
            
            st.subheader("After-Hours Usage")
            if 'is_after_hours' in completed.columns:
                after_hours_count = completed['is_after_hours'].sum()
                total_count = len(completed)
                st.metric("After-Hours Trips", 
                         f"{after_hours_count} ({after_hours_count/total_count*100:.1f}%)" if total_count > 0 else "0")
    else:
        st.info("No performance data available yet.")

with tab4:
    st.header("Trip Routes Map View")
    
    if trips_data:
        trip_options = [f"{t['trip_number']} - {t.get('driver_name', 'Unknown')}" 
                       for t in trips_data]
        
        if trip_options:
            selected_trip_str = st.selectbox("Select a trip to view route", trip_options)
            selected_index = trip_options.index(selected_trip_str)
            selected_trip = trips_data[selected_index]
            
            trip_id = selected_trip['id']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Trip Number:** {selected_trip['trip_number']}")
                st.write(f"**Driver:** {selected_trip.get('driver_name', 'Unknown')}")
                st.write(f"**Status:** {selected_trip['status']}")
            
            with col2:
                st.write(f"**Distance:** {selected_trip.get('distance_travelled', 'N/A')} km")
                st.write(f"**Duration:** {selected_trip.get('duration_minutes', 'N/A')} min")
                st.write(f"**Route Compliance:** {selected_trip.get('route_compliance', 'N/A')}%")
            
            start_lat = selected_trip.get('start_location_lat')
            start_lng = selected_trip.get('start_location_lng')
            end_lat = selected_trip.get('end_location_lat')
            end_lng = selected_trip.get('end_location_lng')
            
            if start_lat and start_lng:
                m = folium.Map(location=[float(start_lat), float(start_lng)], zoom_start=12)
                
                folium.Marker(
                    [float(start_lat), float(start_lng)],
                    popup="Start Location",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(m)
                
                if end_lat and end_lng:
                    folium.Marker(
                        [float(end_lat), float(end_lng)],
                        popup="End Location",
                        icon=folium.Icon(color='red', icon='stop')
                    ).add_to(m)
                    
                    folium.PolyLine(
                        [[float(start_lat), float(start_lng)], 
                         [float(end_lat), float(end_lng)]],
                        color='blue',
                        weight=3,
                        opacity=0.7
                    ).add_to(m)
                
                try:
                    gps_points = fetch_data(f"trips/{trip_id}/gps-route")
                    if gps_points:
                        coordinates = [[float(p['latitude']), float(p['longitude'])] 
                                     for p in gps_points]
                        folium.PolyLine(
                            coordinates,
                            color='red',
                            weight=2,
                            opacity=0.8,
                            popup="Actual Route"
                        ).add_to(m)
                except:
                    pass
                
                st_folium(m, width=700, height=500)
            else:
                st.info("No GPS data available for this trip.")
    else:
        st.info("No trips available to display on map.")

st.sidebar.header("About")
st.sidebar.info(
    "This dashboard displays real-time fleet management data including "
    "trip statistics, driver performance, and route visualization."
)
