from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS: разрешаем запросы с твоего фронта на Vercel ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lyvo.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # превью Vercel (опционально)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

# Приём данных от Mini App
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    # Здесь пока просто логируем, потом будем сохранять/обрабатывать
    print("MiniApp event:", data)
    return {"received": True, "echo": data}