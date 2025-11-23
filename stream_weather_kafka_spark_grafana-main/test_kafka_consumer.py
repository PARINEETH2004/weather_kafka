from kafka import KafkaConsumer
import json

def consume_test_messages():
    # Kafka Consumer
    consumer = KafkaConsumer(
        'weather_topic',
        bootstrap_servers=['localhost:9093'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='test-consumer-group',
        api_version=(0, 10, 1)
    )
    
    print("Starting test consumer...")
    print("Listening for messages on 'weather_topic'...")
    print("-" * 50)
    
    try:
        for message in consumer:
            data = message.value
            print("Received message:")
            print(json.dumps(data, indent=2))
            print("-" * 50)
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_test_messages()