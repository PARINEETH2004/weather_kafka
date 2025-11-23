from kafka import KafkaProducer
import json

def send_simple_message():
    try:
        # Create producer with explicit IPv4 address
        producer = KafkaProducer(
            bootstrap_servers=['127.0.0.1:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print("Producer connected successfully")
        
        # Send a simple message
        message = {"test": "simple message", "value": 42}
        future = producer.send('weather_topic', message)
        result = future.get(timeout=10)
        print(f"Message sent successfully: {result}")
        
        # Close producer
        producer.close()
        print("Producer closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_simple_message()