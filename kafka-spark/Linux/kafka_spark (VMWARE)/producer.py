from kafka import KafkaProducer
import json
import time
import csv

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "transactions"

with open("transactions.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = {
            "id": row["id"],
            "amount": float(row["amount"]),
            "location": row["location"]
        }
        producer.send(topic, value=data)
        print(f"Sent: {data}")
        time.sleep(1)  
producer.flush()
producer.close()