import streamlit as st
import json
import threading
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from kafka import KafkaConsumer
from collections import defaultdict, deque
from datetime import datetime
import requests

# Set page config with modern theme
st.set_page_config(
    page_title="Live Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for modern UI with vibrant colors
st.markdown("""
<style>
    /* Modern vibrant color scheme */
    :root {
        --primary: #FF6B6B;        /* Red */
        --secondary: #4ECDC4;      /* Teal */
        --accent: #FFD166;         /* Yellow */
        --dark: #1A535C;           /* Dark Teal */
        --darker: #0D3B40;         /* Even Darker Teal */
        --light: #F7FFF7;          /* Light Green/White */
        --success: #6BCB77;        /* Green */
        --warning: #FF6B6B;        /* Red */
        --info: #4D9DE0;           /* Blue */
        --purple: #9C89B8;         /* Purple */
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
        color: var(--light);
    }
    
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent) !important;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Card styling with vibrant borders */
    .css-1r6slb0, .css-12w0qpk, .css-1kyxreq {
        background: rgba(26, 83, 92, 0.7) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
        border: 2px solid var(--secondary);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .css-1r6slb0:hover, .css-12w0qpk:hover, .css-1kyxreq:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(78, 205, 196, 0.4);
    }
    
    /* Button styling with vibrant colors */
    .stButton>button {
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
        background: linear-gradient(45deg, #ff5252, #4bc9c4);
    }
    
    /* Input styling with colorful borders */
    .stTextInput>div>div>input {
        background: rgba(13, 59, 64, 0.7);
        border: 2px solid var(--secondary);
        border-radius: 12px;
        color: var(--light);
        font-size: 16px;
        padding: 12px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(255, 209, 102, 0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox>div>div {
        background: rgba(13, 59, 64, 0.7);
        border: 2px solid var(--secondary);
        border-radius: 12px;
        color: var(--light);
        font-size: 16px;
    }
    
    .stSelectbox>div>div:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(255, 209, 102, 0.3);
    }
    
    /* Metric styling with vibrant backgrounds */
    .stMetric {
        background: linear-gradient(135deg, rgba(26, 83, 92, 0.8) 0%, rgba(13, 59, 64, 0.8) 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid var(--primary);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.2);
    }
    
    .stMetric-label {
        color: var(--accent) !important;
        font-weight: 600;
        font-size: 18px;
    }
    
    .stMetric-value {
        color: var(--light) !important;
        font-weight: 800;
        font-size: 28px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(26, 83, 92, 0.7);
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid var(--secondary);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: rgba(13, 59, 64, 0.9);
        backdrop-filter: blur(15px);
        border-right: 3px solid var(--secondary);
    }
    
    /* Plotly chart background */
    .js-plotly-plot .plotly {
        background: rgba(13, 59, 64, 0.5) !important;
        border-radius: 15px;
        border: 2px solid var(--secondary);
    }
    
    /* Custom styles for city tags */
    .city-tag {
        background: linear-gradient(45deg, var(--primary), var(--accent));
        color: var(--darker);
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        margin: 5px;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);
    }
    
    /* Status indicators */
    .status-success {
        color: var(--success);
        font-weight: 600;
    }
    
    .status-warning {
        color: var(--warning);
        font-weight: 600;
    }
    
    .status-info {
        color: var(--info);
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(13, 59, 64, 0.5);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 83, 92, 0.7);
        border-radius: 10px;
        color: var(--light);
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Live update indicator */
    .live-update {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Use Streamlit's cache to store data globally
@st.cache_resource
def get_data_storage():
    """Create a thread-safe data storage object"""
    return {
        'weather_data_store': {},
        'recent_data': deque(maxlen=100),
        'cities_data': {},
        'lock': threading.Lock(),
        'last_data_update': time.time()
    }

# Get the global data storage
data_storage = get_data_storage()

# Initialize session state for UI
if 'monitored_cities' not in st.session_state:
    st.session_state.monitored_cities = set()
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None

# Kafka consumer function with better error handling
def consume_kafka_data():
    """Consume weather data from Kafka and update global storage"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            consumer = KafkaConsumer(
                'weather_topic',
                bootstrap_servers=['127.0.0.1:9093'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=f'weather-dashboard-group-streamlit-{int(time.time())}',
                api_version=(0, 10, 1),
                request_timeout_ms=30000,
                heartbeat_interval_ms=3000,
                session_timeout_ms=10000
            )
            
            print("Kafka consumer started, listening for weather data...")
            
            # Consume messages
            for message in consumer:
                try:
                    data = message.value
                    
                    # DEBUG: Print raw data for debugging
                    print(f"Raw data received: {data}")
                    
                    # Extract city information
                    city_name = data.get('name', 'Unknown')
                    if not city_name or city_name == 'Unknown':
                        # Use coordinates if name is not available
                        city_name = f"{data['coord']['lat']:.2f},{data['coord']['lon']:.2f}"
                    
                    # Convert temperature from Kelvin to Celsius
                    temp_celsius = data['main']['temp'] - 273.15
                    
                    # Process weather data
                    weather_info = {
                        'city': city_name,
                        'temperature': round(temp_celsius, 1),
                        'feels_like': round(data['main'].get('feels_like', temp_celsius) - 273.15, 1),
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure'],
                        'description': data['weather'][0]['description'].title(),
                        'main_condition': data['weather'][0]['main'],
                        'wind_speed': data.get('wind', {}).get('speed', 0),
                        'wind_direction': data.get('wind', {}).get('deg', 0),
                        'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'clouds': data.get('clouds', {}).get('all', 0),
                        'rain_1h': data.get('rain', {}).get('1h', 0),
                        'snow_1h': data.get('snow', {}).get('1h', 0)
                    }
                    
                    # Thread-safe update of global storage
                    with data_storage['lock']:
                        data_storage['weather_data_store'][city_name] = weather_info
                        data_storage['recent_data'].append(weather_info)
                        data_storage['cities_data'][city_name] = weather_info
                        data_storage['last_data_update'] = time.time()
                    
                    print(f"Updated data for {city_name}: {weather_info['temperature']}°C, {weather_info['description']}")
                    
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in Kafka consumer: {e}")
            retry_count += 1
            time.sleep(5)  # Wait before retrying
            continue

# Start Kafka consumer in background thread
@st.cache_resource
def start_kafka_consumer():
    consumer_thread = threading.Thread(target=consume_kafka_data, daemon=True)
    consumer_thread.start()
    return consumer_thread

# Start the Kafka consumer
start_kafka_consumer()

# Helper functions to access data safely
def get_weather_data_store():
    with data_storage['lock']:
        return data_storage['weather_data_store'].copy()

def get_recent_data():
    with data_storage['lock']:
        return list(data_storage['recent_data'])

def get_cities_data():
    with data_storage['lock']:
        return data_storage['cities_data'].copy()

def get_last_data_update_time():
    with data_storage['lock']:
        return data_storage['last_data_update']

# Main app
def main():
    # Modern header with vibrant colors
    st.markdown("<h1 style='text-align: center; margin-bottom: 0; font-size: 3rem;'>🌤️ Live Weather Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--accent); margin-top: 0; font-size: 1.3rem; font-weight: 600;'>Real-time weather data streaming from Kafka</p>", unsafe_allow_html=True)
    
    # Live update indicator
    last_update = get_last_data_update_time()
    time_since_update = time.time() - last_update
    if time_since_update < 5:  # If data was updated in the last 5 seconds
        st.markdown("<p style='text-align: center; color: var(--success); font-weight: 700;' class='live-update'>● LIVE DATA STREAMING ●</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center; color: var(--warning); font-weight: 700;'>● CONNECTING TO DATA STREAM ●</p>", unsafe_allow_html=True)
    
    # Manual refresh button (no auto-refresh that causes full page reload)
    st.sidebar.markdown("### <span style='color: var(--accent); font-size: 1.3rem; font-weight: 700;'>Controls</span>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 Refresh Data"):
        st.experimental_rerun()
    
    # Show last update time
    st.sidebar.markdown(f"<p class='status-info'>Last data update: {datetime.fromtimestamp(last_update).strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    # Debug information
    weather_data_store = get_weather_data_store()
    recent_data = get_recent_data()
    
    st.sidebar.markdown("### <span style='color: var(--accent); font-size: 1.3rem; font-weight: 700;'>Debug Info</span>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='color: var(--success); font-weight: 600; font-size: 1.1rem;'>Cities in store: {len(weather_data_store)}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='color: var(--info); font-weight: 600; font-size: 1.1rem;'>Recent data points: {len(recent_data)}</p>", unsafe_allow_html=True)
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🌡️ Current Weather", "📊 Trends", "🏙️ All Cities"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Current weather display with modern cards
            st.subheader("🌡️ Current Weather")
            
            # Display weather data for selected city
            display_city = None
            if st.session_state.selected_city and st.session_state.selected_city in weather_data_store:
                display_city = st.session_state.selected_city
            elif weather_data_store:
                # If no city is selected, show the first available city
                display_city = list(weather_data_store.keys())[0]
            
            if display_city and display_city in weather_data_store:
                data = weather_data_store[display_city]
                
                # Main weather card with vibrant styling
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(26, 83, 92, 0.8) 0%, rgba(13, 59, 64, 0.8) 100%); 
                            border-radius: 20px; 
                            padding: 30px; 
                            text-align: center; 
                            border: 3px solid var(--accent);
                            box-shadow: 0 10px 30px rgba(255, 209, 102, 0.3);">
                    <h2 style="margin: 0; color: var(--accent); font-size: 2.5rem;">{data['city']}</h2>
                    <h3 style="margin: 15px 0; color: var(--primary); font-size: 3rem;">{data['temperature']}°C</h3>
                    <p style="font-size: 1.5rem; margin: 0; color: var(--light);">{data['description']}</p>
                    <p style="color: var(--secondary); margin: 10px 0; font-size: 1.2rem;">Feels like {data['feels_like']}°C</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Weather metrics in a grid
                st.markdown("### Weather Details")
                temp_col, feels_col, humidity_col, wind_col = st.columns(4)
                
                with temp_col:
                    st.metric("🌡️ Temperature", f"{data['temperature']}°C")
                
                with feels_col:
                    st.metric("😊 Feels Like", f"{data['feels_like']}°C")
                
                with humidity_col:
                    st.metric("💧 Humidity", f"{data['humidity']}%")
                
                with wind_col:
                    st.metric("💨 Wind Speed", f"{data['wind_speed']} m/s")
                
                # Additional details
                pressure_col, visibility_col, clouds_col, rain_col = st.columns(4)
                
                with pressure_col:
                    st.metric("📊 Pressure", f"{data['pressure']} hPa")
                
                with visibility_col:
                    st.metric("👁️ Visibility", f"{data['visibility']} km")
                
                with clouds_col:
                    st.metric("☁️ Clouds", f"{data['clouds']}%")
                
                with rain_col:
                    st.metric("🌧️ Rain (1h)", f"{data['rain_1h']} mm")
                
            else:
                st.warning("No weather data available. Please add cities or wait for data to load.")
                st.info("The dashboard is connecting to Kafka stream. Data should appear shortly...")
                if weather_data_store:
                    st.write("Available cities:", list(weather_data_store.keys())[:5])
        
        with col2:
            # City selector and controls
            st.subheader("📍 City Controls")
            
            # Add city section
            with st.form("add_city_form"):
                city_name = st.text_input("Enter city name (e.g., London, Tokyo)", "")
                submitted = st.form_submit_button("📍 Add City")
                if submitted:
                    if city_name:
                        st.session_state.monitored_cities.add(city_name)
                        st.success(f"Added {city_name} to monitored cities!")
                        # Show the added city with vibrant styling
                        st.markdown(f"<div class='city-tag'>{city_name}</div>", unsafe_allow_html=True)
                        # Automatically select the newly added city
                        st.session_state.selected_city = city_name
                    else:
                        st.warning("Please enter a city name")
            
            # ENHANCED: City selection with full control
            st.subheader("🔍 Select City")
            st.markdown("### Available Cities")
            
            # Get all available cities
            available_cities = list(weather_data_store.keys())
            
            if available_cities:
                # Create a more intuitive city selection interface
                st.markdown("#### Quick Select")
                # Create buttons for the first 10 cities for quick selection
                cols = st.columns(5)
                for i, city in enumerate(available_cities[:10]):
                    with cols[i % 5]:
                        if st.button(f"{city}", key=f"city_btn_{i}"):
                            st.session_state.selected_city = city
                            st.experimental_rerun()
                
                st.markdown("#### Search & Select")
                # Search box for cities
                search_term = st.text_input("Search cities...", "")
                
                # Filter cities based on search term
                if search_term:
                    filtered_cities = [city for city in available_cities if search_term.lower() in city.lower()]
                else:
                    filtered_cities = available_cities
                
                # Dropdown with filtered cities
                if filtered_cities:
                    # Set default index based on selected city
                    default_index = 0
                    if st.session_state.selected_city and st.session_state.selected_city in filtered_cities:
                        default_index = filtered_cities.index(st.session_state.selected_city)
                    
                    selected = st.selectbox("Choose a city", filtered_cities, index=default_index, key="city_selector")
                    st.session_state.selected_city = selected
                    
                    # Highlight selected city
                    st.markdown(f"<div class='city-tag'>{selected}</div>", unsafe_allow_html=True)
                else:
                    st.info("No cities match your search.")
                
                # Display current selection
                if st.session_state.selected_city:
                    st.markdown(f"### Currently Viewing: <span class='city-tag'>{st.session_state.selected_city}</span>", unsafe_allow_html=True)
                
                # Add a "Clear Selection" button
                if st.button("🔄 Clear Selection"):
                    st.session_state.selected_city = None
                    st.experimental_rerun()
                    
            else:
                st.info("No cities available yet. Waiting for data from Kafka stream...")
            
            # Status panel
            st.subheader("📡 Status")
            st.markdown(f"<p class='status-info'>Last updated: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='status-success'>Active cities: {len(weather_data_store)}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='status-warning'>Monitored cities: {len(st.session_state.monitored_cities)}</p>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📊 Weather Trends")
        
        # Get recent data
        recent_data = get_recent_data()
        st.markdown(f"Debug: Recent data points available: {len(recent_data)}")
        
        # Show raw data structure for debugging
        if recent_data and len(recent_data) > 0:
            sample_data = recent_data[0] if recent_data else {}
            st.markdown("Debug: Sample data structure:")
            st.json(sample_data)
        
        if recent_data and len(recent_data) > 0:
            # Convert deque to list for DataFrame
            df = pd.DataFrame(recent_data)
            
            # DEBUG: Show dataframe info
            st.markdown(f"Debug: DataFrame shape: {df.shape}")
            if not df.empty:
                st.markdown("Debug: DataFrame columns: " + ", ".join(df.columns))
                st.markdown("Debug: DataFrame head:")
                st.dataframe(df.head())
            
            # Ensure we have enough data points for meaningful visualization
            if len(df) >= 2:  # Need at least 2 points to draw a line
                # Check if we have the required columns for plotting
                required_columns = ['timestamp', 'temperature', 'humidity', 'wind_speed', 'city']
                if all(col in df.columns for col in required_columns):
                    # Temperature trend with modern styling
                    st.markdown("### 🌡️ Temperature Trends (°C)")
                    fig_temp = px.line(df, x='timestamp', y='temperature', color='city',
                                      line_shape='spline', render_mode='svg',
                                      title="Temperature Trends by City")
                    fig_temp.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        title=dict(font=dict(size=20, color='var(--accent)'))
                    )
                    st.plotly_chart(fig_temp, use_container_width=True, theme=None)
                    
                    # Humidity trend
                    st.markdown("### 💧 Humidity Trends (%)")
                    fig_humidity = px.line(df, x='timestamp', y='humidity', color='city',
                                          line_shape='spline', render_mode='svg',
                                          title="Humidity Trends by City")
                    fig_humidity.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        title=dict(font=dict(size=20, color='var(--accent)'))
                    )
                    st.plotly_chart(fig_humidity, use_container_width=True, theme=None)
                    
                    # Wind speed trend
                    st.markdown("### 💨 Wind Speed Trends (m/s)")
                    fig_wind = px.line(df, x='timestamp', y='wind_speed', color='city',
                                      line_shape='spline', render_mode='svg',
                                      title="Wind Speed Trends by City")
                    fig_wind.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        title=dict(font=dict(size=20, color='var(--accent)'))
                    )
                    st.plotly_chart(fig_wind, use_container_width=True, theme=None)
                else:
                    st.error("Missing required data columns for plotting.")
                    st.write("Available columns:", df.columns.tolist() if not df.empty else [])
                    st.write("Required columns:", required_columns)
                    # Show the actual data structure
                    if not df.empty:
                        st.write("Sample data row:")
                        st.json(df.iloc[0].to_dict())
            else:
                st.info(f"Need at least 2 data points to show trends. Currently have {len(df)} points.")
                st.info("The dashboard is collecting more data points. Charts will appear shortly...")
                
                # Show what data we do have
                if not df.empty:
                    st.markdown("### Current Data Points")
                    st.dataframe(df)
        else:
            st.info("Waiting for weather data to populate charts...")
            st.info("The dashboard is connecting to Kafka stream. Data should appear shortly...")
            
            # Add some debugging information
            weather_data_store = get_weather_data_store()
            st.markdown(f"Debug: Cities in store: {len(weather_data_store)}")
            if weather_data_store:
                st.markdown("Debug: Sample cities: " + ", ".join(list(weather_data_store.keys())[:5]))

    with tab3:
        st.subheader("🏙️ All Monitored Cities")
        if weather_data_store:
            cities_df = pd.DataFrame(weather_data_store.values())
            # Display as a modern table
            st.dataframe(cities_df[['city', 'temperature', 'humidity', 'pressure', 'description']].style
                        .set_properties(**{'background-color': 'rgba(26, 83, 92, 0.7)', 
                                        'color': 'var(--light)', 
                                        'border': '2px solid var(--secondary)',
                                        'font-weight': '600'})
                        .set_table_styles([
                            {'selector': 'th', 'props': [('background-color', 'linear-gradient(45deg, var(--primary), var(--secondary))'), 
                                                        ('color', 'white'), 
                                                        ('font-weight', '700'),
                                                        ('font-size', '1.1rem')]},
                        ]),
                        use_container_width=True, height=600)
                        
            # Display cities with vibrant tags
            st.markdown("### 📍 City Tags")
            city_tags_html = ""
            for city in list(weather_data_store.keys())[:20]:  # Limit to first 20 cities
                city_tags_html += f"<div class='city-tag'>{city}</div>"
            st.markdown(city_tags_html, unsafe_allow_html=True)
        else:
            st.info("No cities data available yet")
            st.info("The dashboard is connecting to Kafka stream. Data should appear shortly...")

if __name__ == "__main__":
    main()