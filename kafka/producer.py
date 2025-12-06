import csv
import json
import time
import random
import os
from kafka import KafkaProducer
from datetime import datetime

# Configuration
KAFKA_TOPIC = 'fitbit_wellness_stream'
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

# Use absolute paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
# We'll focus on the main activity file for the stream simulation
INPUT_FILE = 'dailyActivity_merged.csv'

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            api_version=(0, 10, 1) # Force version if auto-negotiation fails
        )
        print("Kafka Producer created successfully.")
        return producer
    except Exception as e:
        print(f"Error creating Kafka Producer: {e}")
        return None

def read_and_produce(producer, file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found. Please ensure data is in {DATA_DIR}")
        return

    print(f"Streaming data from {file_path} to topic {KAFKA_TOPIC}...")
    
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Add a simulated timestamp for ingestion time
            row['ingestion_timestamp'] = datetime.now().isoformat()
            
            # Send to Kafka
            producer.send(KAFKA_TOPIC, value=row)
            
            # Simulate real-time delay (randomized for effect)
            # In a real scenario, this might be based on the actual time difference in the data
            # But for a demo, a small sleep makes it look like a stream
            time.sleep(random.uniform(0.1, 0.5)) 
            
            print(f"Sent record for User: {row.get('Id', 'Unknown')}")

    producer.flush()
    print("Finished streaming.")

if __name__ == "__main__":
    producer = create_producer()
    if producer:
        file_path = os.path.join(DATA_DIR, INPUT_FILE)
        read_and_produce(producer, file_path)
        producer.close()
