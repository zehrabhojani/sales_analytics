"""Extract-Transform-Load pipeline: validates raw order CSV data, loads clean rows to SQLite,
and writes rejected rows with reasons. `lambda_handler` follows the AWS Lambda signature so the same
code can be wired to an S3 trigger (S3 deployment is not included here)."""
import csv, io, logging, sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("etl")

def extract(text: str):
    return list(csv.DictReader(io.StringIO(text)))

def validate(row: dict):
    """Return (clean_row, None) or (None, reason)."""
    try:
        oid = int(row["order_id"])
        qty = int(row["quantity"])
        price = float(row["unit_price"])
        datetime.strptime(row["order_date"], "%Y-%m-%d")
    except (KeyError, ValueError, TypeError) as e:
        return None, f"invalid field: {e}"
    if not row.get("customer", "").strip():
        return None, "missing customer"
    if qty <= 0 or price < 0:
        return None, "non-positive quantity or negative price"
    return {"order_id": oid, "customer": row["customer"].strip().title(),
            "order_date": row["order_date"], "quantity": qty, "unit_price": price,
            "total": round(qty * price, 2)}, None

def transform(rows):
    clean, rejects, seen = [], [], set()
    for r in rows:
        ok, reason = validate(r)
        if ok and ok["order_id"] in seen:
            ok, reason = None, "duplicate order_id"
        if ok:
            seen.add(ok["order_id"]); clean.append(ok)
        else:
            rejects.append({**r, "reason": reason})
    return clean, rejects

def load(clean, db="warehouse.db"):
    with sqlite3.connect(db) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS orders_clean(order_id INTEGER PRIMARY KEY,
            customer TEXT, order_date TEXT, quantity INTEGER, unit_price REAL, total REAL)""")
        conn.executemany("INSERT OR REPLACE INTO orders_clean VALUES(:order_id,:customer,:order_date,:quantity,:unit_price,:total)", clean)

def run(text, db="warehouse.db"):
    clean, rejects = transform(extract(text))
    load(clean, db)
    log.info("loaded=%d rejected=%d", len(clean), len(rejects))
    return {"loaded": len(clean), "rejected": rejects}

def lambda_handler(event, context=None):
    return run(event["csv_text"])

if __name__ == "__main__":
    sample = open("sample_orders.csv").read()
    res = run(sample)
    for r in res["rejected"]:
        print("REJECTED:", r["order_id"], "-", r["reason"])
