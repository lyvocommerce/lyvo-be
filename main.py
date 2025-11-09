# main.py — Lyvo Backend (FastAPI + Neon)
# Endpoints:
#   GET  /            -> health/info
#   GET  /health      -> health ping
#   GET  /categories  -> list of product categories (from DB)
#   GET  /products    -> catalog with filters/sorting/pagination (from DB)
#   POST /webhook     -> receive events from Mini App
#   POST /auth        -> Telegram authentication check

import os
from typing import Optional, Tuple

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg import OperationalError

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
DATABASE_URL = os.environ["DATABASE_URL"]
FRONT_URL = os.getenv("WEBAPP_URL", "https://lyvo-shop.vercel.app")

# -----------------------------------------------------------------------------
# FastAPI + CORS
# -----------------------------------------------------------------------------
app = FastAPI(title="Lyvo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_URL],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Connection Pool (psycopg v3) + auto-reconnect
# -----------------------------------------------------------------------------
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={"sslmode": "require"},
    min_size=1,
    max_size=5,
    open=True,
)

def safe_connection():
    global pool
    try:
        return pool.connection()
    except OperationalError:
        print("⚠️  Recreating DB connection pool after SSL disconnect...")
        pool.close()
        pool = ConnectionPool(
            conninfo=DATABASE_URL,
            kwargs={"sslmode": "require"},
            min_size=1,
            max_size=5,
            open=True,
        )
        return pool.connection()

# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "lyvo-be"}

@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def build_filters(
    q: Optional[str],
    category: Optional[str],
    merchant: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float],
) -> Tuple[str, list]:
    where, params = [], []
    if q:
        where.append("(title ILIKE %s OR description ILIKE %s)")
        like = f"%{q}%"
        params += [like, like]
    if category:
        where.append("category = %s")
        params.append(category)
    if merchant:
        where.append("merchant_id = %s")
        params.append(merchant)
    if min_price is not None:
        where.append("price_min >= %s")
        params.append(min_price)
    if max_price is not None:
        where.append("price_min <= %s")
        params.append(max_price)
    clause = "WHERE " + " AND ".join(where) if where else ""
    return clause, params


def build_order(sort: Optional[str]) -> str:
    if sort == "price_asc":
        return "ORDER BY price_min ASC NULLS LAST"
    if sort == "price_desc":
        return "ORDER BY price_min DESC NULLS LAST"
    if sort == "popular":
        return "ORDER BY title ASC"
    return "ORDER BY created_at DESC"

# -----------------------------------------------------------------------------
# Categories
# -----------------------------------------------------------------------------
@app.get("/categories")
def get_categories():
    with safe_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL AND category <> ''
                ORDER BY 1;
            """)
            cats = [row[0] for row in cur.fetchall()]
    return {"items": cats}

# -----------------------------------------------------------------------------
# Products
# -----------------------------------------------------------------------------
@app.get("/products")
def get_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: Optional[str] = Query(None, pattern="^(price_asc|price_desc|newest|popular)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
):
    clause, params = build_filters(q, category, merchant, min_price, max_price)
    order_sql = build_order(sort)
    offset = (page - 1) * page_size

    count_sql = f"SELECT COUNT(*) FROM products {clause};"
    list_sql = f"""
        SELECT id, title, description, url, image_url,
               price_min, price_max, currency,
               merchant_id, category, lang, created_at
        FROM products
        {clause}
        {order_sql}
        LIMIT %s OFFSET %s;
    """

    with safe_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()[0]

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(list_sql, params + [page_size, offset])
            items = cur.fetchall()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items,
    }

# -----------------------------------------------------------------------------
# Webhook (Mini App events)
# -----------------------------------------------------------------------------
@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    print("MiniApp event:", data)
    return {"ok": True, "echo": data}

# -----------------------------------------------------------------------------
# Telegram Auth — FINAL version with double-decoding fix
# -----------------------------------------------------------------------------
import hmac, hashlib, urllib.parse, json

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.post("/auth")
async def telegram_auth(req: Request):
    data = await req.json()
    init_data = data.get("initData", "")
    if not init_data:
        return {"ok": False, "error": "missing initData"}

    print("\n=== RAW initData (before parsing) ===")
    print(repr(init_data))
    print("=====================================\n")

    # 🩵 Попробуем двойное декодирование + fix escaped slashes
    decoded = urllib.parse.unquote(init_data)
    decoded = decoded.replace("\\/", "/")

    parsed = dict(urllib.parse.parse_qsl(decoded, keep_blank_values=True))
    check_hash = parsed.pop("hash", None)
    parsed.pop("signature", None)

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    # ✅ по спецификации: secret_key = HMAC_SHA256("WebAppData", bot_token)
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    print("\n=== Telegram Auth Debug ===")
    print("BOT_TOKEN length:", len(BOT_TOKEN))
    print("data_check_string:", data_check_string)
    print("check_hash:", check_hash)
    print("computed_hash:", computed_hash)
    print("equal:", computed_hash == check_hash)
    print("===========================")

    if not hmac.compare_digest(computed_hash, check_hash):
        print("⚠️ Hash mismatch — likely browser or wrong BOT_TOKEN or escaped chars")
        return {"ok": False, "error": "invalid hash"}

    user_json = parsed.get("user")
    try:
        user = json.loads(user_json) if user_json else None
    except json.JSONDecodeError:
        print("⚠️ JSON decode error in user field")
        user = None

    print("✅ Telegram Auth OK —", user.get("username") if user else "unknown")
    return {"ok": True, "user": user}