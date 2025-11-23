import json
import time
import os

def consume_weather_data():
    print("Starting weather data consumer...")
    print("This is a simplified version that reads from a file instead of Kafka")
    print("-" * 50)
    
    # In a real scenario, this would consume from Kafka
    # For demonstration, we'll just show how the data would be processed
    sample_data = {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "weather": [{"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"}],
        "base": "stations",
        "main": {
            "temp": 297.96,
            "feels_like": 298.61,
            "temp_min": 297.96,
            "temp_max": 297.96,
            "pressure": 1015,
            "humidity": 81
        },
        "visibility": 10000,
        "wind": {"speed": 4.84, "deg": 186, "gust": 4.6},
        "clouds": {"all": 100},
        "dt": 1762075889,
        "sys": {"sunrise": 1762062005, "sunset": 1762105617},
        "timezone": 0,
        "id": 6295630,
        "name": "London",
        "cod": 200
    }
    
    print("Sample weather data processed:")
    print(json.dumps(sample_data, indent=2))
    print("-" * 50)
    print("In a real implementation with Kafka and Spark:")
    print("1. Kafka would stream the weather data")
    print("2. Spark would process the streaming data")
    print("3. Processed data would be sent to Grafana for visualization")

if __name__ == "__main__":
    consume_weather_data()