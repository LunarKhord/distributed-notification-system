import json
import aio_pika
from typing import Any, Dict
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)





async def push_to_queue(rabbit_mq_channel:aio_pika.Channel, notification: Dict[str, Any]):
    """
    Acts as the primary ingress point for message dissemination. 
    
    This function orchestrates the serialization of the notification 
    payload and coordinates its transmission to the RabbitMQ exchange. 
    It leverages the 'notification_type' attribute within the dictionary 
    to derive the appropriate routing key, ensuring the message is 
    channeled to the correct downstream consumer.
    """
    logger.info(f"Preparing to push notification to queue: {notification}")
    notification_type = notification.get('notification_type').value
    logger.info(f"Notification type: {notification_type}")

    # Here you would implement the logic to push the notification
    # to the RabbitMQ exchange using the appropriate routing key.
    if notification_type == 'email':
        await email_queue_push(rabbit_mq_channel, notification)
    elif notification_type == 'sms':
        await sms_queue_push(rabbit_mq_channel, notification)
    elif notification_type == 'push_notification':
        await push_notification_queue_push(rabbit_mq_channel, notification)
    else:
        logger.error(f"Unknown notification type: {notification_type}")
        raise ValueError(f"Unknown notification type: {notification_type}")
        return None


async def publish_message(channel: aio_pika.Channel, routing_key: str, message_body: Dict[str, Any]):
    try:
        print("Channel in publish_message:", channel)
        logger.info(f"Publishing message was called by the queue push function for routing key: {routing_key}")
        # Step 1: Normalize the payload (Crucial for Enums and HttpUrls)
        # If message_body is a Pydantic model, use message_body.model_dump(mode='json')
        # Otherwise, handle manual conversion:
        print("Message body before normalization:", message_body)
        normalized_body = json.loads(json.dumps(message_body, default=str))
        print("Normalized message body:", normalized_body)

        try:
            exchange = await channel.declare_exchange(name="api-gateway-direct", type="direct", durable=True)
        except Exception as e:
            logger.error(f"Failed to declare exchange: {str(e)}")
            return False
        print("Declared exchange:", exchange)
        priority_level = int(normalized_body.get("priority", 0))
        print("Priority level:", priority_level)
        message = aio_pika.Message(
            body=json.dumps(normalized_body).encode("utf-8"),
            priority=priority_level,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json"
        )
        print("Prepared message:", message)
        # Step 2: Ensure the publish call is truly awaited
        await exchange.publish(message, routing_key=routing_key)
        
        logger.info(f"Message published successfully to {routing_key}")
        return True

    except Exception as e:
        logger.error(f"Critical failure in publish_message: {str(e)}")
        # Raise or return False so the API knows to stop waiting
        return False

async def email_queue_push(rabbit_mq_channel:aio_pika.Channel, notification: Dict[str, Any]):
    """
    Specifically encapsulates the logic for dispatching electronic 
    mail payloads.
    
    This specialized routine handles the nuances of the 'email' 
    routing key and ensures that the message metadata (such as 
    content-type or priority headers) is configured to optimize 
    throughput for the SMTP-focused worker services.
    """
    ROUTING_KEY = "email"
    logger.info("Push to email queue initiated.")
    # Implement the logic to push the email notification to RabbitMQ Email Queue
    response = await publish_message(rabbit_mq_channel, ROUTING_KEY, notification)
    return response

async def sms_queue_push(rabbit_mq_channel:aio_pika.Channel, notification: Dict[str, Any]):
    """
    Operationalizes the transmission of Short Message Service (SMS) data. 
    
    Given the temporal sensitivity and potential rate-limiting 
    constraints of telephony gateways, this function manages the 
    interfacing with the 'sms' exchange binding, prioritizing 
    delivery reliability over high-volume batching.
    """
    ROUTING_KEY = "sms"

    logger.info("Push to SMS queue initiated.")
    # Implement the logic to push the SMS notification to RabbitMQ SMS Queue
    response = await publish_message(rabbit_mq_channel, ROUTING_KEY, notification)


async def push_notification_queue_push(rabbit_mq_channel:aio_pika.Channel, notification: Dict[str, Any]):
    """
    Manages the dispatch of ephemeral push notifications for 
    mobile or web interfaces. 
    
    This function targets the 'push_notification' routing key, 
    facilitating the delivery of real-time alerts. It is designed 
    to handle the high-concurrency demands inherent in user-facing 
    mobile application signaling.
    """
    ROUTING_KEY = "push_notification"

    logger.info("Push to Push Notification queue initiated.")
    # Implement the logic to push the Push Notification to RabbitMQ Push Notification Queue
    response = await publish_message(rabbit_mq_channel, ROUTING_KEY, notification)
