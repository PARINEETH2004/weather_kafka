from flask import Flask, render_template, jsonify
import json
import threading
import time
from kafka import KafkaConsumer
from collections import defaultdict, deque
from datetime import datetime

app = Flask(__name__)

# Global data storage
weather_data_store = defaultdict(dict)
recent_data = deque(maxlen=50)  # Store recent data points for charts
cities_data = defaultdict(dict)  # Store data by city

# Kafka consumer thread
def consume_kafka_data():
    """Consume weather data from Kafka and update global storage"""
    try:
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['127.0.0.1:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='weather-dashboard-group-flask',
            api_version=(0, 10, 1)
        )
        
        print("Kafka consumer started, listening for weather data...")
        
        for message in consumer:
            try:
                data = message.value
                
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
                
                # Update global storage
                weather_data_store[city_name] = weather_info
                recent_data.append(weather_info)
                cities_data[city_name] = weather_info
                
                print(f"Updated data for {city_name}: {weather_info['temperature']}°C, {weather_info['description']}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
                
    except Exception as e:
        print(f"Error in Kafka consumer: {e}")

# Start Kafka consumer in background thread
consumer_thread = threading.Thread(target=consume_kafka_data, daemon=True)
consumer_thread.start()

@app.route('/')
def dashboard():
    """Render the main dashboard page"""
    return render_template('flask_dashboard.html')

@app.route('/api/current')
def current_weather():
    """API endpoint to get current weather data"""
    # Return the most recent data for all cities
    return jsonify(dict(weather_data_store))

@app.route('/api/recent')
def recent_weather():
    """API endpoint to get recent weather data for charts"""
    return jsonify(list(recent_data))

@app.route('/api/cities')
def cities_list():
    """API endpoint to get list of monitored cities"""
    return jsonify(list(cities_data.keys()))

@app.route('/api/city/<city_name>')
def city_weather(city_name):
    """API endpoint to get weather data for a specific city"""
    if city_name in weather_data_store:
        return jsonify(weather_data_store[city_name])
    else:
        return jsonify({'error': 'City not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)