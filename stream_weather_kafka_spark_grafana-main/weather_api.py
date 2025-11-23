from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import json
from kafka import KafkaConsumer, KafkaProducer
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store weather data in memory (in production, you would use a database)
weather_data = {}
active_alerts = []
monitored_cities = set()  # Cities we're actively monitoring

# Kafka producer for sending city requests
producer = None

def init_kafka_producer():
    """Initialize Kafka producer"""
    global producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print("Kafka producer initialized")
    except Exception as e:
        print(f"Failed to initialize Kafka producer: {e}")

def consume_weather_data():
    """Consume weather data from Kafka and store it in memory"""
    global weather_data, active_alerts
    
    # Kafka Consumer
    consumer = KafkaConsumer(
        'weather_topic',
        bootstrap_servers=['localhost:9093'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='weather-dashboard-group',
        api_version=(0, 10, 1)  # Explicitly set API version
    )
    
    print("Starting weather data consumer for dashboard...")
    
    try:
        for message in consumer:
            data = message.value
            
            # Extract city name or use coordinates if name is not available
            city_name = data.get('name', f"{data['coord']['lat']},{data['coord']['lon']}")
            
            # Only process data for monitored cities (or all if no cities are specifically monitored)
            if not monitored_cities or city_name in monitored_cities:
                # Convert temperature from Kelvin to Celsius
                temp_celsius = data['main']['temp'] - 273.15
                
                # Store the data
                weather_data[city_name] = {
                    'temperature': round(temp_celsius, 1),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'rainfall': data.get('rain', {}).get('1h', 0)  # Rain volume for last 1 hour
                }
                
                # Check for alerts
                check_for_alerts(city_name, weather_data[city_name])
                
                print(f"Updated weather data for {city_name}")
            
    except Exception as e:
        print(f"Error in Kafka consumer: {e}")
    finally:
        consumer.close()

def check_for_alerts(city_name, data):
    """Check weather data for potential alerts"""
    global active_alerts
    
    # Remove old alerts for this city
    active_alerts = [alert for alert in active_alerts if alert['city'] != city_name]
    
    # Temperature alerts
    if data['temperature'] > 35:
        active_alerts.append({
            'city': city_name,
            'type': 'heat',
            'message': f'Extreme heat warning in {city_name}: {data["temperature"]}°C',
            'severity': 'high'
        })
    elif data['temperature'] < 0:
        active_alerts.append({
            'city': city_name,
            'type': 'cold',
            'message': f'Freezing conditions in {city_name}: {data["temperature"]}°C',
            'severity': 'medium'
        })
    
    # Rainfall alerts
    if data['rainfall'] > 30:
        active_alerts.append({
            'city': city_name,
            'type': 'flood',
            'message': f'Heavy rainfall in {city_name}: {data["rainfall"]}mm in the last hour',
            'severity': 'high'
        })
    elif data['rainfall'] > 15:
        active_alerts.append({
            'city': city_name,
            'type': 'rain',
            'message': f'Moderate rainfall in {city_name}: {data["rainfall"]}mm',
            'severity': 'medium'
        })
    
    # Wind alerts
    if data['wind_speed'] > 20:
        active_alerts.append({
            'city': city_name,
            'type': 'wind',
            'message': f'High winds in {city_name}: {data["wind_speed"]} m/s',
            'severity': 'medium'
        })
    
    # Pressure alerts (might indicate approaching storm)
    if data['pressure'] < 1000:
        active_alerts.append({
            'city': city_name,
            'type': 'pressure',
            'message': f'Low pressure system in {city_name}: {data["pressure"]} hPa',
            'severity': 'low'
        })

@app.route('/api/weather')
def get_weather_data():
    """Return all weather data"""
    return jsonify(weather_data)

@app.route('/api/weather/<city>')
def get_city_weather(city):
    """Return weather data for a specific city"""
    if city in weather_data:
        return jsonify({city: weather_data[city]})
    else:
        return jsonify({'error': 'City not found'}), 404

@app.route('/api/alerts')
def get_alerts():
    """Return active alerts"""
    return jsonify(active_alerts)

@app.route('/api/cities')
def get_cities():
    """Return list of monitored cities"""
    return jsonify(list(weather_data.keys()))

@app.route('/api/monitor/city', methods=['POST'])
def add_city_to_monitor():
    """Add a city to the monitoring list"""
    global producer
    
    try:
        data = request.get_json()
        city_name = data.get('city')
        
        if not city_name:
            return jsonify({'error': 'City name is required'}), 400
        
        # Add to monitored cities
        monitored_cities.add(city_name)
        
        # In a full implementation, we would send a message to the weather producer
        # to start fetching data for this city
        # For now, we'll just acknowledge the request
        
        return jsonify({'message': f'City {city_name} added to monitoring list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/cities', methods=['GET'])
def get_monitored_cities():
    """Get list of all monitored cities"""
    return jsonify(list(monitored_cities))

if __name__ == '__main__':
    # Initialize Kafka producer
    init_kafka_producer()
    
    # Start Kafka consumer in a separate thread
    consumer_thread = threading.Thread(target=consume_weather_data, daemon=True)
    consumer_thread.start()
    
    # Run the Flask app
    app.run(host='localhost', port=5000, debug=True, use_reloader=False)