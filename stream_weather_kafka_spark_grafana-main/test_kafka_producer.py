from kafka import KafkaProducer
import json
import time

def send_test_message():
    # Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9093'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    
    # Send a test message
    test_message = {
        "name": "Test City",
        "main": {
            "temp": 293.15,  # 20°C in Kelvin
            "humidity": 65,
            "pressure": 1013
        },
        "weather": [
            {
                "main": "Clear",
                "description": "clear sky"
            }
        ],
        "wind": {
            "speed": 3.5
        }
    }
    
    try:
        producer.send('weather_topic', test_message)
        producer.flush()
        print("Test message sent successfully!")
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    send_test_message()