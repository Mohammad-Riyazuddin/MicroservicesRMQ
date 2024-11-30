import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_events")

def publish_event(event_type, payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    message = {"event_type": event_type, "payload": payload}
    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=json.dumps(message))
    connection.close()
