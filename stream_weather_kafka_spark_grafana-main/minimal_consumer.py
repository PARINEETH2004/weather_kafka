from kafka import KafkaConsumer
import json

# Minimal Kafka Consumer
consumer = KafkaConsumer(
    'weather_topic',
    bootstrap_servers=['localhost:9093'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='minimal-group',
    api_version=(0, 10, 1)
)

print("Minimal consumer started, waiting for messages...")

try:
    for message in consumer:
        print(f"Received: {message.value}")
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    consumer.close()