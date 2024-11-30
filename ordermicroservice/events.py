import pika
import json
from database import orders_collection

def handle_event(ch, method, properties, body):
    try:
        # Log the received message
        print(f"Received event: {body}")

        # Parse the message body
        event = json.loads(body)

        # Handle the specific event type
        if event["event_type"] == "user_updated":
            payload = event["payload"]

            # Debug log for payload
            print(f"Processing payload: {payload}")

            # Update the orders in MongoDB
            result = orders_collection.update_many(
                {"user_id": payload["user_id"]},  # Match user_id
                {
                    "$set": {
                        "email": payload["email"],
                        "delivery_address": payload["delivery_address"]
                    }
                }
            )

            # Log the result of the update operation
            print(f"Matched {result.matched_count} documents, Modified {result.modified_count} documents.")

    except Exception as e:
        # Log any exceptions
        print(f"Error handling event: {e}")

# Establish connection to RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declare the queue (ensure it exists)
    channel.queue_declare(queue='user_events')

    # Start consuming messages
    channel.basic_consume(queue='user_events', on_message_callback=handle_event, auto_ack=True)
    print("Order Microservice is listening for events...")
    channel.start_consuming()

except Exception as e:
    print(f"Error connecting to RabbitMQ: {e}")
