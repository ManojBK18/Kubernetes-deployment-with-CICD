import os
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException

app = FastAPI()

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
        CREATE TABLE IF NOT EXISTS analytics (
            id         SERIAL PRIMARY KEY,
            code       VARCHAR(10) NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()


@app.post("/click/{code}")
def record_click(code: str):
    """Called by the API Gateway every time a short URL is accessed."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO analytics (code) VALUES (%s)", (code,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "recorded"}


@app.get("/analytics/{code}")
def get_analytics(code: str):
    """Returns click count, creation time, and last accessed time for a code."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Total click count
    cur.execute("SELECT COUNT(*) as click_count FROM analytics WHERE code = %s", (code,))
    count_row = cur.fetchone()

    # Last accessed time
    cur.execute(
        "SELECT clicked_at FROM analytics WHERE code = %s ORDER BY clicked_at DESC LIMIT 1",
        (code,)
    )
    last_row = cur.fetchone()

    # Creation time (from the urls table — shared DB, both services access it)
    cur.execute("SELECT created_at FROM urls WHERE code = %s", (code,))
    url_row = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "code": code,
        "click_count": count_row["click_count"],
        "last_accessed": last_row["clicked_at"].isoformat() if last_row else None,
        "created_at": url_row["created_at"].isoformat() if url_row else None,
    }


# Health check endpoint — used for K8s liveness/readiness probes
@app.get("/health")
def health():
    return {"status": "ok", "service": "analytics"}
