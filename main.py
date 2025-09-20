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

# --- Catalog demo (categories + products) ---
import json, math
from pathlib import Path
from fastapi import Query

DATA_PATH = Path(__file__).parent / "data" / "products_demo.json"
PRODUCTS = []

def load_products():
    global PRODUCTS
    try:
        PRODUCTS = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        PRODUCTS = []
        print("Failed to load demo products:", e)

@app.on_event("startup")
def _load_on_start():
    load_products()

def list_categories():
    cats = sorted({p.get("category", "other") for p in PRODUCTS})
    return cats

@app.get("/categories")
def get_categories():
    return {"items": list_categories()}

@app.get("/products")
def get_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort: str | None = Query(None, pattern="^(price_asc|price_desc|newest|popular)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
):
    items = PRODUCTS[:]

    # фильтры
    if category:
        items = [p for p in items if p.get("category") == category]
    if q:
        s = q.strip().lower()
        items = [
            p for p in items
            if s in p.get("title","").lower() or s in p.get("desc","").lower() or s in p.get("brand","").lower()
        ]
    if min_price is not None:
        items = [p for p in items if float(p.get("price", 0)) >= min_price]
    if max_price is not None:
        items = [p for p in items if float(p.get("price", 0)) <= max_price]

    # сортировка
    if sort == "price_asc":
        items.sort(key=lambda p: float(p.get("price", 0)))
    elif sort == "price_desc":
        items.sort(key=lambda p: float(p.get("price", 0)), reverse=True)
    elif sort == "popular":
        items.sort(key=lambda p: float(p.get("rating", 0)), reverse=True)
    elif sort == "newest":
        # у демо нет даты — оставляем как есть; позже добавим поле date
        pass

    # пагинация
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    items_page = items[start:end]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items_page,
    }