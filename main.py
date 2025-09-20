# main.py — Lyvo Backend (FastAPI)
# Endpoints:
#   GET  /            -> health/info
#   GET  /health      -> health ping
#   GET  /categories  -> list of product categories
#   GET  /products    -> catalog with filters/sorting/pagination
#   POST /webhook     -> receive events from Mini App

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------------------------------------------------------
# FastAPI app + CORS
# -----------------------------------------------------------------------------
app = FastAPI(title="Lyvo Backend")

# Frontend URL (for CORS)
FRONT_URL = os.getenv("WEBAPP_URL", "https://lyvo.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_URL],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Health endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    """Return basic service info."""
    return {"status": "ok", "service": "lyvo-be"}

@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok"}

# -----------------------------------------------------------------------------
# Demo catalog
# -----------------------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "data" / "products_demo.json"
PRODUCTS: List[Dict[str, Any]] = []

def load_products() -> None:
    """Load demo products from JSON file."""
    global PRODUCTS
    try:
        if DATA_PATH.exists():
            PRODUCTS = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        else:
            PRODUCTS = []
    except Exception as e:
        print("Failed to load demo products:", e)
        PRODUCTS = []

@app.on_event("startup")
def on_startup():
    """Load data when the service starts."""
    load_products()

def list_categories() -> List[str]:
    """Extract unique categories from products."""
    return sorted({p.get("category", "other") for p in PRODUCTS})

@app.get("/categories")
def get_categories():
    """Return list of categories."""
    return {"items": list_categories()}

@app.get("/products")
def get_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: Optional[str] = Query(None, pattern="^(price_asc|price_desc|newest|popular)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
):
    """Return products with optional filters, sorting and pagination."""
    items = PRODUCTS[:]

    # Filtering
    if category:
        items = [p for p in items if p.get("category") == category]
    if q:
        needle = q.strip().lower()
        items = [
            p for p in items
            if needle in (p.get("title", "").lower())
            or needle in (p.get("desc", "").lower())
            or needle in (p.get("brand", "").lower())
        ]
    if min_price is not None:
        items = [p for p in items if float(p.get("price", 0)) >= float(min_price)]
    if max_price is not None:
        items = [p for p in items if float(p.get("price", 0)) <= float(max_price)]

    # Sorting
    if sort == "price_asc":
        items.sort(key=lambda p: float(p.get("price", 0)))
    elif sort == "price_desc":
        items.sort(key=lambda p: float(p.get("price", 0)), reverse=True)
    elif sort == "popular":
        items.sort(key=lambda p: float(p.get("rating", 0)), reverse=True)
    elif sort == "newest":
        pass  # demo data has no date

    # Pagination
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

# -----------------------------------------------------------------------------
# Webhook (Mini App events)
# -----------------------------------------------------------------------------
@app.post("/webhook")
async def webhook(req: Request):
    """
    Receive data from the Telegram Mini App via tg.sendData().
    For now: log and echo back the payload.
    """
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")

    print("MiniApp event:", data)  # visible in Render logs
    return {"ok": True, "echo": data}