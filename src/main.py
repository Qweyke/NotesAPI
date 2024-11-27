from fastapi import FastAPI
from uvicorn import Config, Server

from src.counter_manager import CounterManager
from src.router import app_router

app = FastAPI()
app.include_router(app_router)

COUNTER_PATH = "notes/counter.txt"
counter_manager = CounterManager(COUNTER_PATH)

if __name__ == "__main__":
    config = Config(app=app, host="127.0.0.1", port=8000, reload=True)
    server = Server(config)
    server.run()
