# Running the Complete Weather Streaming System

This document explains how to run the complete weather streaming system including Kafka, Spark, and the new dashboard.

## Prerequisites

1. Java JDK 8 or higher
2. Python 3.7+
3. Apache Kafka
4. The required Python packages (see [requirements.txt](file:///c%3A/Users/PARINEETH/Downloads/stream_weather_kafka_spark_grafana-main/stream_weather_kafka_spark_grafana-main/requirements.txt))

## Setup Instructions

### 1. Start Zookeeper

Open a terminal and run:
```bash
# Windows
.\zookeeper-server-start.bat .\config\zookeeper.properties

# Linux/Mac
./zookeeper-server-start.sh ./config/zookeeper.properties
```

### 2. Start Kafka Server

Open another terminal and run:
```bash
# Windows
.\kafka-server-start.bat .\config\server.properties

# Linux/Mac
./kafka-server-start.sh ./config/server.properties
```

### 3. Create Kafka Topic

Create the weather topic:
```bash
# Windows
.\kafka-topics.bat --create --topic weather_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Linux/Mac
./kafka-topics.sh --create --topic weather_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 4. Run the Weather Data Producer

In a new terminal, run the weather producer:
```bash
python weather_kafka_producer.py
```

### 5. Run the Dashboard Backend API

In a new terminal, run the dashboard API:
```bash
python weather_api.py
```

### 6. Open the Dashboard

Open [weather_dashboard.html](file:///c%3A/Users/PARINEETH/Downloads/stream_weather_kafka_spark_grafana-main/stream_weather_kafka_spark_grafana-main/weather_dashboard.html) in your web browser.

## System Components

### Weather Data Flow

1. `weather_kafka_producer.py` - Fetches weather data from OpenWeatherMap API and sends it to Kafka
2. Kafka - Message broker that handles the data stream
3. `weather_api.py` - Consumes data from Kafka and serves it to the dashboard
4. `weather_dashboard.html` - Frontend dashboard that visualizes the data

### Data Visualization

The dashboard provides real-time visualizations of:
- Temperature trends across cities
- Rainfall data with color-coded severity
- Humidity levels
- Wind speed distribution
- Storm alerts with different severity levels

### Adding Cities

To add a new city to monitor:
1. Enter the city name in the input field at the top of the dashboard
2. Click "Add City" or press Enter
3. The city will be added to the monitoring list
4. Weather data for the city will appear when available

## Troubleshooting

### Common Issues

1. **Port already in use**: If you see port conflicts, make sure no other instances are running:
   ```bash
   # Windows
   netstat -ano | findstr :9092
   taskkill /PID <PID> /F
   ```

2. **Kafka connection issues**: Make sure Zookeeper is running before starting Kafka

3. **API connection errors**: Ensure the weather_api.py is running on port 5000

### Logs

Check the terminal outputs for each component to diagnose issues:
- Kafka logs will show in the Kafka server terminal
- Producer logs will show in the weather_kafka_producer.py terminal
- API logs will show in the weather_api.py terminal

## Customization

### Weather Data

To use your own OpenWeatherMap API key:
1. Get an API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Replace the API key in `weather_kafka_producer.py`

### Dashboard

You can customize the dashboard by modifying:
- `dashboard_styles.css` - Visual styling
- `dashboard_script.js` - JavaScript functionality
- `weather_api.py` - Backend API endpoints and data processing

See [DASHBOARD_README.md](file:///c%3A/Users/PARINEETH/Downloads/stream_weather_kafka_spark_grafana-main/stream_weather_kafka_spark_grafana-main/DASHBOARD_README.md) for more details on dashboard customization.