from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logging
import aio_pika


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP PHASE ---
    try:
        logger.info("Initiating persistent RabbitMQ bridge...")
        # 1. Establish the Robust Connection (No 'async with' here!)
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@rabbitmq/", 
            heartbeat=60
        )
        
        # 2. Open the Channel
        channel = await connection.channel()

        # 3. Declare Topology (Exchange and Queues)
        exchange = await channel.declare_exchange(
            name="api-gateway-direct", 
            type=aio_pika.ExchangeType.DIRECT, 
            durable=True
        )

        email_queue = await channel.declare_queue(name="email-queue", durable=True)
        sms_queue = await channel.declare_queue(name="sms-queue", durable=True)
        push_notification_queue = await channel.declare_queue(name="push-notification-queue", durable=True)

        await email_queue.bind(exchange, routing_key="email")
        await sms_queue.bind(exchange, routing_key="sms")
        await push_notification_queue.bind(exchange, routing_key="push_notification")

        # 4. Anchor to Application State (This prevents Garbage Collection)
        app.state.rabbit_mq_connection = connection
        app.state.rabbit_mq_channel = channel
        app.state.exchange = exchange
        
        logger.info("RabbitMQ bridge successfully anchored to Application State.")

    except Exception as rabbitMQError:
        logger.error(f"Failed to establish RabbitMQ topology: {rabbitMQError}")
        # Consider if the app should even start if the message broker is down
        raise rabbitMQError 

    yield  # --- APPLICATION IS NOW ACTIVE AND SERVING REQUESTS ---

    # --- SHUTDOWN PHASE ---
    logger.info("Severing RabbitMQ bridge...")
    if not app.state.rabbit_mq_connection.is_closed:
        await app.state.rabbit_mq_connection.close()



async def get_rabbit_mq_connection(request: Request):
    return request.app.state.rabbit_mq_connection

async def get_rabbit_mq_exchange(request: Request):
    return request.app.state.exchange


async def get_rabbit_mq_channel(request: Request):
    return request.app.state.rabbit_mq_channel


app = FastAPI(title="API-Gateway", lifespan=lifespan)