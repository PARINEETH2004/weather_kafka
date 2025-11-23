from kafka import KafkaProducer
import json
import time

def test_producer():
    # Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9093'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)  # Explicitly set API version
    )
    
    print("Starting test producer...")
    
    # Send a test message
    test_data = {
        "name": "Test City",
        "main": {
            "temp": 293.15,  # 20°C
            "humidity": 65,
            "pressure": 1013
        },
        "weather": [
            {
                "main": "Clear",
                "description": "clear sky"
            }
        ]
    }
    
    try:
        future = producer.send('weather_topic', test_data)
        # Wait for the send to complete
        record_metadata = future.get(timeout=10)
        print(f"✓ Test message sent to weather_topic")
        print(f"  Topic: {record_metadata.topic}")
        print(f"  Partition: {record_metadata.partition}")
        print(f"  Offset: {record_metadata.offset}")
    except Exception as e:
        print(f"✗ Failed to send test message: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    test_producer()