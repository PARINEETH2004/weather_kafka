from kafka import KafkaConsumer
import json
import time

def consume_weather_data():
    # Kafka Consumer with unique group ID
    consumer = KafkaConsumer(
        'weather_topic',
        bootstrap_servers=['127.0.0.1:9093'],  # Use explicit IPv4 address
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # Changed to earliest to get all messages
        enable_auto_commit=True,
        group_id=f'weather-group-{int(time.time())}',
        api_version=(0, 10, 1)
    )
    
    print("Starting weather data consumer...")
    print("Bootstrap servers:", consumer.config['bootstrap_servers'])
    print("Topic subscription:", consumer.subscription())
    print("Listening for weather data on 'weather_topic'...")
    print("-" * 50)
    
    try:
        for message in consumer:
            weather_data = message.value
            print(f"Received weather data:")
            print(f"  Location: {weather_data.get('name', 'Unknown')}")
            # Convert temperature from Kelvin to Celsius
            if 'main' in weather_data and 'temp' in weather_data['main']:
                temp_celsius = weather_data['main']['temp'] - 273.15
                print(f"  Temperature: {temp_celsius:.1f}°C")
            print(f"  Weather: {weather_data.get('weather', [{}])[0].get('main', 'Unknown')} - {weather_data.get('weather', [{}])[0].get('description', 'Unknown')}")
            print(f"  Humidity: {weather_data.get('main', {}).get('humidity', 'N/A')}%")
            print(f"  Pressure: {weather_data.get('main', {}).get('pressure', 'N/A')} hPa")
            # Check for wind data
            if 'wind' in weather_data:
                print(f"  Wind Speed: {weather_data['wind'].get('speed', 'N/A')} m/s")
            # Check for rainfall data
            if 'rain' in weather_data:
                rainfall = weather_data['rain'].get('1h', 'N/A')
                print(f"  Rainfall (1h): {rainfall} mm")
            print("-" * 50)
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_weather_data()