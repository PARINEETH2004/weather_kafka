from kafka import KafkaConsumer
import json

def test_consumer():
    # Kafka Consumer
    consumer = KafkaConsumer(
        'weather_topic',
        bootstrap_servers=['localhost:9093'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='test-consumer-group',
        api_version=(0, 10, 1)  # Explicitly set API version
    )
    
    print("Starting test consumer...")
    print("Listening for weather data on 'weather_topic'...")
    print("-" * 50)
    
    try:
        for message in consumer:
            weather_data = message.value
            print(f"Received weather data:")
            print(f"  Location: {weather_data.get('name', 'Unknown')}")
            # Convert temperature from Kelvin to Celsius
            temp_celsius = weather_data['main']['temp'] - 273.15
            print(f"  Temperature: {temp_celsius:.1f}°C")
            print(f"  Weather: {weather_data['weather'][0]['main']} - {weather_data['weather'][0]['description']}")
            print(f"  Humidity: {weather_data['main']['humidity']}%")
            print(f"  Pressure: {weather_data['main']['pressure']} hPa")
            print("-" * 50)
            break  # Just show one message and exit
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    test_consumer()