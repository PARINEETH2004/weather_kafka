from kafka import KafkaProducer, KafkaConsumer
import json
import time
import threading

def send_and_receive_test():
    print("=== Kafka Send and Receive Test ===")
    
    # Create a consumer in a separate thread
    def consume_messages():
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=f'test-group-{int(time.time())}',
            api_version=(0, 10, 1)
        )
        
        print("Consumer started, waiting for messages...")
        try:
            for message in consumer:
                print(f"✓ Consumer received: {message.value}")
                break  # Exit after receiving one message
        except Exception as e:
            print(f"Consumer error: {e}")
        finally:
            consumer.close()
    
    # Start consumer thread
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.start()
    
    # Wait a moment for consumer to start
    time.sleep(2)
    
    # Send a test message
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        
        test_message = {
            "test": "send_receive_test",
            "timestamp": time.time(),
            "value": "Hello Kafka!"
        }
        
        producer.send('weather_topic', test_message)
        producer.flush()
        print("✓ Producer sent test message")
        producer.close()
        
    except Exception as e:
        print(f"Producer error: {e}")
    
    # Wait for consumer thread to finish
    consumer_thread.join(timeout=10)
    print("Test completed")

if __name__ == "__main__":
    send_and_receive_test()