import os, requests
import psycopg
from psycopg.rows import dict_row

DB_URL = os.environ["DATABASE_URL"]
MERCHANT_ID = "lyvo"

def fetch_products():
    print("🔄 Fetching products from DummyJSON...")
    res = requests.get("https://dummyjson.com/products?limit=100", timeout=30)
    res.raise_for_status()
    return res.json()["products"]

def normalize(p):
    return {
        "id": f"dummy-{p['id']}",
        "title": p.get("title"),
        "description": p.get("description") or "",
        "url": f"https://dummyjson.com/products/{p['id']}",
        "image_url": p.get("thumbnail") or (p.get("images") or [None])[0],
        "price_min": float(p.get("price", 0)),
        "currency": "EUR",
        "merchant_id": MERCHANT_ID,
        "category": p.get("category"),
        "lang": "en",
    }

def import_products():
    # sslmode=require на Neon обязателен
    with psycopg.connect(DB_URL, sslmode="require") as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) AS c FROM products;")
            print(f"🧾 Before import: {cur.fetchone()['c']} products")

            products = [normalize(p) for p in fetch_products()]

            cur.executemany("""
                INSERT INTO products
                (id, title, description, url, image_url, price_min, currency, merchant_id, category, lang)
                VALUES
                (%(id)s, %(title)s, %(description)s, %(url)s, %(image_url)s, %(price_min)s,
                 %(currency)s, %(merchant_id)s, %(category)s, %(lang)s)
                ON CONFLICT (id) DO UPDATE SET
                  title = EXCLUDED.title,
                  description = EXCLUDED.description,
                  url = EXCLUDED.url,
                  image_url = EXCLUDED.image_url,
                  price_min = EXCLUDED.price_min,
                  currency = EXCLUDED.currency,
                  merchant_id = EXCLUDED.merchant_id,
                  category = EXCLUDED.category,
                  lang = EXCLUDED.lang;
            """, products)

            conn.commit()
            print(f"✅ Imported/updated {len(products)} products.")

if __name__ == "__main__":
    import_products()