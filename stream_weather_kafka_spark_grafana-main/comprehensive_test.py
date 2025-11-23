from kafka import KafkaProducer, KafkaConsumer
import json
import time

def test_complete_flow():
    print("Testing complete Kafka flow...")
    
    try:
        # Create producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print("Producer created successfully")
        
        # Create consumer
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['localhost:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='comprehensive-test-group-' + str(int(time.time())),
            api_version=(0, 10, 1)
        )
        print("Consumer created successfully")
        
        # Send test message
        test_message = {
            "name": "Comprehensive Test City",
            "main": {
                "temp": 295.15,  # 22°C in Kelvin
                "humidity": 70,
                "pressure": 1015
            },
            "weather": [
                {
                    "main": "Clouds",
                    "description": "scattered clouds"
                }
            ],
            "wind": {
                "speed": 4.2
            }
        }
        
        print("Sending test message...")
        future = producer.send('weather_topic', test_message)
        producer.flush()
        print("Test message sent!")
        
        # Wait a bit for the message to be processed
        time.sleep(2)
        
        # Try to consume the message
        print("Attempting to consume message...")
        messages = consumer.poll(timeout_ms=10000)  # 10 second timeout
        
        if not messages:
            print("No messages received!")
        else:
            print(f"Received {len(messages)} message sets")
            for topic_partition, message_list in messages.items():
                print(f"Topic partition: {topic_partition}")
                for message in message_list:
                    data = message.value
                    print("Received message:")
                    print(json.dumps(data, indent=2))
        
        # Close connections
        consumer.close()
        producer.close()
        print("Test completed")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_flow()