from fastapi import FastAPI
import os

app = FastAPI()

# Чисто для проверки, что BE жив
@app.get("/")
def ping():
    return {"status": "ok"}

# Читаем переменные окружения с Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "")

# (дальше будем наращивать ендпойнты; пока это MVP)