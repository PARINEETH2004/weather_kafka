from kafka import KafkaProducer
import requests
import json
import time
import random

# Function to fetch weather data
def get_weather_data():
    api_key = "b8bfddab1e0d47c54a08d4dd861d44b6"
    random_lat_lon = generate_random_lat_lon()

    # Use HTTPS instead of HTTP
    url = f"https://api.openweathermap.org/data/2.5/weather?" \
      f"lat={random_lat_lon[0]}&lon={random_lat_lon[1]}" \
      f"&appid={api_key}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to weather API: {e}")
        return None

def generate_random_lat_lon():
    # Latitude ranges from -90 to 90
    latitude = random.uniform(-90, 90)
    # Longitude ranges from -180 to 180
    longitude = random.uniform(-180, 180)
    return latitude, longitude

def produce_weather_data():
    # Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9093'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)  # Explicitly set API version
    )
        
    while True:
        weather_data = get_weather_data()
        if weather_data:
            producer.send('weather_topic', weather_data)
            print(f"Sent: {weather_data}")
        else:
            print("Failed to get weather data, retrying in 10 seconds...")
        time.sleep(10)  # Fetch data every 10 seconds


if __name__ == "__main__":
  produce_weather_data()