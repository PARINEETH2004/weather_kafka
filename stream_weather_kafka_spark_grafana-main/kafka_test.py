from kafka import KafkaConsumer, KafkaProducer
import json

def test_kafka():
    print("Testing Kafka connection...")
    
    # Test 1: Check if we can create a producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            api_version=(0, 10, 1)
        )
        print("✓ Kafka producer created successfully")
        producer.close()
    except Exception as e:
        print(f"✗ Failed to create Kafka producer: {e}")
        return
    
    # Test 2: Check if we can create a consumer and list topics
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=['localhost:9093'],
            api_version=(0, 10, 1),
            group_id='test-group'
        )
        print("✓ Kafka consumer created successfully")
        
        # List available topics
        topics = consumer.topics()
        print(f"Available topics: {topics}")
        
        consumer.close()
    except Exception as e:
        print(f"✗ Failed to create Kafka consumer: {e}")
        return

if __name__ == "__main__":
    test_kafka()