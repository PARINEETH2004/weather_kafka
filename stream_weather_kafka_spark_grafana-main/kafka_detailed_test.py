from kafka import KafkaConsumer, KafkaProducer
import json
import time

def detailed_kafka_test():
    print("=== Kafka Detailed Test ===")
    
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
        test_msg = {"test": "message", "timestamp": time.time()}
        future = producer.send('weather_topic', test_msg)
        record_metadata = future.get(timeout=10)
        print(f"✓ Message sent - Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
        producer.close()
        
    except Exception as e:
        print(f"✗ Producer test failed: {e}")
        return
    
    # Test 2: Consumer
    print("\n2. Testing Kafka Consumer...")
    try:
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='test-group-detailed',
            api_version=(0, 10, 1)
        )
        print("✓ Consumer created successfully")
        
        # Check partitions
        partitions = consumer.partitions_for_topic('weather_topic')
        print(f"✓ Partitions: {partitions}")
        
        # Poll for messages with timeout
        print("Polling for messages (5 seconds)...")
        messages = consumer.poll(timeout_ms=5000, max_records=10)
        
        if messages:
            print(f"✓ Received {len(messages)} message sets")
            for topic_partition, msgs in messages.items():
                print(f"  Partition {topic_partition.partition}: {len(msgs)} messages")
                for msg in msgs:
                    print(f"    Message: {msg.value}")
        else:
            print("✗ No messages received within 5 seconds")
            
        consumer.close()
        
    except Exception as e:
        print(f"✗ Consumer test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_kafka_test()