import json
from google.cloud import pubsub_v1

project_id = "labs-data-engineering-457205"
topic_id = "MyTopic"
topic_path = pubsub_v1.PublisherClient().topic_path(project_id, topic_id)

publisher = pubsub_v1.PublisherClient()

with open("bcsample.json", "r") as f:
    breadcrumb_data = json.load(f)  

count = 0
for record in breadcrumb_data:
    count+=1
    data_str = json.dumps(record)  
    data = data_str.encode("utf-8")  
    future = publisher.publish(topic_path, data)

print(f"Published {len(breadcrumb_data)} messages to {topic_path}.")
