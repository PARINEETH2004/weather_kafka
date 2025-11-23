from kafka import KafkaConsumer, KafkaProducer
import json
import time

def simple_kafka_test():
    print("=== Simple Kafka Test ===")
    
    # Test 1: Producer
    print("\n1. Testing Kafka Producer...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print("✓ Producer created successfully")
        
        # Send test message
        test_msg = {"test": "simple_test_message", "timestamp": time.time(), "value": 42}
        producer.send('weather_topic', test_msg)
        producer.flush()
        print("✓ Message sent to weather_topic")
        producer.close()
        
    except Exception as e:
        print(f"✗ Producer test failed: {e}")
        return
    
    # Test 2: Consumer (using iterator with timeout)
    print("\n2. Testing Kafka Consumer...")
    try:
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='simple-test-group-' + str(int(time.time())),
            api_version=(0, 10, 1)
        )
        print("✓ Consumer created successfully")
        
        # Check partitions
        partitions = consumer.partitions_for_topic('weather_topic')
        print(f"✓ Partitions: {partitions}")
        
        print("Waiting for messages (10 seconds)...")
        
        # Set a timeout for the consumer
        start_time = time.time()
        timeout = 10
        
        # Try to get one message
        try:
            message = next(consumer)
            print(f"✓ Received message: {message.value}")
        except StopIteration:
            print("✗ No messages received")
        except Exception as e:
            print(f"✗ Error receiving message: {e}")
                
        consumer.close()
        
    except Exception as e:
        print(f"✗ Consumer test failed: {e}")

if __name__ == "__main__":
    simple_kafka_test()