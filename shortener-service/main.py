import os
import string
import random
import redis
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Redis client — host will be a K8s Service name in cluster
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# PostgreSQL connection — host will be a K8s Service name in cluster
def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "urlshortener"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            code        VARCHAR(10) PRIMARY KEY,
            original_url TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


class ShortenRequest(BaseModel):
    url: str


@app.post("/shorten")
def shorten(req: ShortenRequest):
    code = generate_code()
    conn = get_db()
    cur = conn.cursor()

    # Ensure the generated code is unique
    while True:
        cur.execute("SELECT code FROM urls WHERE code = %s", (code,))
        if not cur.fetchone():
            break
        code = generate_code()

    cur.execute(
        "INSERT INTO urls (code, original_url) VALUES (%s, %s)",
        (code, req.url)
    )
    conn.commit()
    cur.close()
    conn.close()

    # Cache in Redis with 1 hour TTL
    redis_client.setex(f"url:{code}", 3600, req.url)

    return {"code": code, "short_url": f"/r/{code}", "original_url": req.url}


@app.get("/resolve/{code}")
def resolve(code: str):
    # Check Redis cache first (fast path)
    cached = redis_client.get(f"url:{code}")
    if cached:
        return {"url": cached, "source": "cache"}

    # Fall back to PostgreSQL (slow path)
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT original_url FROM urls WHERE code = %s", (code,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Code not found")

    # Re-populate cache for next time
    redis_client.setex(f"url:{code}", 3600, row["original_url"])
    return {"url": row["original_url"], "source": "db"}


# Health check endpoint — used for K8s liveness/readiness probes
@app.get("/health")
def health():
    return {"status": "ok", "service": "shortener"}
