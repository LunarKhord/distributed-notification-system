from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {"health": "OK"}




@app.post("/api/v1/notifications/")
async def create_notification(notification: dict):