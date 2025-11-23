from kafka import KafkaProducer, KafkaConsumer
import json
import time

def basic_kafka_test():
    print("=== Basic Kafka Test ===")
    
    # Send a test message
    print("\n1. Sending test message...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        
        test_message = {
            "test": "basic_kafka_test",
            "timestamp": time.time(),
            "message": "Hello Kafka!"
        }
        
        producer.send('weather_topic', test_message)
        producer.flush()
        print("✓ Test message sent successfully")
        producer.close()
        
    except Exception as e:
        print(f"✗ Failed to send message: {e}")
        return
    
    # Receive the test message
    print("\n2. Receiving test message...")
    try:
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=f'basic-test-group-{int(time.time())}',
            api_version=(0, 10, 1)
        )
        
        # Poll for messages
        messages = consumer.poll(timeout_ms=5000, max_records=1)
        
        if messages:
            for topic_partition, msgs in messages.items():
                for msg in msgs:
                    print(f"✓ Received message: {msg.value}")
        else:
            print("✗ No messages received within timeout")
            
        consumer.close()
        
    except Exception as e:
        print(f"✗ Failed to receive message: {e}")

if __name__ == "__main__":
    basic_kafka_test()