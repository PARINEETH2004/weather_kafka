# Weather Dashboard

A real-time weather dashboard that visualizes temperature, rainfall, and storm alerts with the ability to add cities dynamically.

## Features

- Real-time weather data visualization
- Temperature, humidity, rainfall, and wind speed charts
- Storm alerts system with severity levels
- Dynamic city management (add/remove cities)
- Responsive design that works on desktop and mobile devices

## Prerequisites

- Python 3.7+
- Kafka server running on localhost:9093
- The main weather streaming system should be running (weather_kafka_producer.py)

## Installation

1. Install required Python packages:
   ```bash
   pip install flask flask-cors
   ```

2. Make sure the Kafka server is running with the proper configuration

3. Ensure the weather data producer is running:
   ```bash
   python weather_kafka_producer.py
   ```

## Running the Dashboard

1. Start the backend API:
   ```bash
   python weather_api.py
   ```

2. Open `weather_dashboard.html` in your web browser

## Usage

1. The dashboard will automatically connect to the backend API and display weather data for monitored cities
2. To add a new city, enter the city name in the input field and click "Add City"
3. Weather data will be displayed in real-time with visualizations
4. Storm alerts will appear in the alerts section with different severity levels:
   - High (red): Extreme weather conditions
   - Medium (orange): Moderate weather warnings
   - Low (yellow): Minor weather notices

## Visualizations

- **Temperature Trends**: Line chart showing temperature data across cities
- **Rainfall Data**: Bar chart with color-coded rainfall amounts
- **Humidity Levels**: Radar chart displaying humidity percentages
- **Wind Speed**: Doughnut chart showing wind speed distribution
- **Storm Alerts**: Real-time alert system with automatic updates

## API Endpoints

- `GET /api/weather` - Get all weather data
- `GET /api/weather/<city>` - Get weather data for a specific city
- `GET /api/alerts` - Get active storm alerts
- `GET /api/cities` - Get list of monitored cities
- `POST /api/monitor/city` - Add a city to the monitoring list

## Architecture

The dashboard consists of:
1. Frontend: HTML/CSS/JavaScript with Chart.js for visualizations
2. Backend: Flask API that consumes data from Kafka
3. Data Source: Kafka topic `weather_topic` with weather data
4. Real-time Updates: WebSocket-like polling every 5 seconds

## Customization

You can customize the dashboard by modifying:
- `dashboard_styles.css` - Visual styling
- `dashboard_script.js` - JavaScript functionality
- `weather_api.py` - Backend API endpoints and data processing