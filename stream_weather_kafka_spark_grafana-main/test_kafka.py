from kafka import KafkaProducer, KafkaConsumer
import json

def test_kafka_connection():
    try:
        # Test producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print("Producer connected successfully")
        
        # Test consumer
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='test-group',
            api_version=(0, 10, 1)
        )
        print("Consumer connected successfully")
        
        # Send a test message
        test_message = {"test": "connection", "status": "success"}
        producer.send('weather_topic', test_message)
        producer.flush()
        print("Test message sent")
        
        consumer.close()
        producer.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_kafka_connection()