# A sample project for using Kafka, Spark and other tools to fetch a weather data and stream it.

## Project Overview
This project demonstrates how to fetch weather data from the OpenWeatherMap API, stream it using Kafka, process it with Spark, and visualize it with a custom real-time dashboard.

## Running the Project
For detailed instructions on how to run the project, please see [RUNNING.md](file:///c%3A/Users/PARINEETH/Downloads/stream_weather_kafka_spark_grafana-main/stream_weather_kafka_spark_grafana-main/RUNNING.md)

## Components
- `weather_kafka_producer.py`: Fetches weather data and sends it to Kafka
- `spark_kafka_consumer.py`: Consumes data from Kafka using Spark Streaming
- `simple_weather_producer.py`: Simplified version for demonstration (no Kafka required)
- `simple_weather_consumer.py`: Simplified version for demonstration (no Kafka required)
- `weather_dashboard.py`: Real-time weather dashboard with visualizations (Python/Tkinter version)
- `weather_api.py`: Backend API that serves weather data to the web dashboard
- `weather_dashboard.html`: Web-based real-time weather dashboard with visualizations
- Configuration files for Kafka, Zookeeper, and Prometheus

## Dashboard Features
The real-time weather dashboard provides:
- Temperature, humidity, pressure, and wind speed visualizations
- Storm alerts with severity levels
- Ability to add cities dynamically
- Real-time data updates from Kafka stream

To use the Python dashboard:
1. Start the system using the instructions in RUNNING.md
2. Run `python weather_dashboard.py`

To use the web dashboard:
1. Start the system using the instructions in RUNNING.md
2. Run `python weather_api.py`
3. Open `weather_dashboard.html` in your web browser
4. Add cities using the input field at the top
5. View real-time weather data and alerts

## Dashboard Documentation
For detailed information about the web dashboard, see [DASHBOARD_README.md](file:///c%3A/Users/PARINEETH/Downloads/stream_weather_kafka_spark_grafana-main/stream_weather_kafka_spark_grafana-main/DASHBOARD_README.md)