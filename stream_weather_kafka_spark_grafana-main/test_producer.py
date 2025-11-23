from kafka import KafkaProducer
import requests
import json
import time

def test_kafka_connection():
    try:
        # Kafka Producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)  # Explicitly set API version
        )
        print("Kafka producer connected successfully!")
        
        # Test sending a simple message
        test_data = {"test": "message", "timestamp": time.time()}
        producer.send('weather_topic', test_data)
        producer.flush()
        print("Test message sent to Kafka!")
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return False

def test_weather_api():
    api_key = "b8bfddab1e0d47c54a08d4dd861d44b6"
    # Test with a fixed location (New York)
    url = f"http://api.openweathermap.org/data/2.5/weather?q=New York&appid={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

if __name__ == "__main__":
    print("Testing Kafka connection...")
    if test_kafka_connection():
        print("\nTesting Weather API...")
        weather_data = test_weather_api()
        if weather_data:
            print("Weather API is working!")
            print(f"City: {weather_data['name']}")
            print(f"Temperature: {weather_data['main']['temp']}K")
        else:
            print("Weather API test failed!")
    else:
        print("Kafka connection test failed!")