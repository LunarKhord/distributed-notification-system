from fastapi import Depends
import aio_pika

from lifespan import app, get_rabbit_mq_connection, get_rabbit_mq_channel
from models.Notification import Notification
from utils.orchestration import push_to_queue



@app.get("/")
async def root():
    return {"health": "OK"}


@app.post("/api/v1/notifications/")
async def create_notification(notification_payload: Notification, rabbit_mq_channel:aio_pika.Channel = Depends(get_rabbit_mq_channel)):

    # Convert Pydantic model to dictionary
    notification_dict = notification_payload.model_dump()
    response = await push_to_queue(rabbit_mq_channel, notification_dict)
    if response is None:
        return {"status": "Failed to create notification"}
    return {"status": "Notification created", "notification": notification_payload }