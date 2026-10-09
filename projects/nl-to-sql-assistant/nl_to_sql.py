"""Natural-language -> SQL assistant over the retail SQLite DB.

Uses the Anthropic API when ANTHROPIC_API_KEY is set; otherwise a small rule-based fallback
so the project runs offline. Every generated query is validated (SELECT only) before running.
"""
import os, re, sqlite3, sys

SCHEMA = """customers(customer_id, name, region, signup_date)
products(product_id, name, category, price)
orders(order_id, customer_id, order_date)
order_items(order_id, product_id, quantity)"""

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace)\b", re.I)

def validate_sql(sql: str) -> str:
    """Allow a single read-only SELECT/WITH statement only."""
    s = sql.strip().rstrip(";")
    if ";" in s:
        raise ValueError("Multiple statements are not allowed")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise ValueError("Only SELECT queries are allowed")
    if FORBIDDEN.search(s):
        raise ValueError("Query contains a forbidden keyword")
    return s

def llm_sql(question: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=400,
        system=f"Translate the question into one read-only SQLite SELECT query. Schema:\n{SCHEMA}\nReturn only SQL.",
        messages=[{"role": "user", "content": question}])
    return re.sub(r"^```(?:sql)?|```$", "", msg.content[0].text.strip(), flags=re.M).strip()

RULES = [
    (r"revenue.*category", "SELECT p.category, ROUND(SUM(oi.quantity*p.price),2) AS revenue FROM order_items oi JOIN products p USING(product_id) GROUP BY p.category ORDER BY revenue DESC"),
    (r"how many customers.*region", "SELECT region, COUNT(*) AS customers FROM customers GROUP BY region"),
    (r"top (\d+) products", None),
    (r"orders.*month", "SELECT substr(order_date,1,7) AS month, COUNT(*) AS orders FROM orders GROUP BY month ORDER BY month"),
]

def rule_sql(question: str) -> str:
    q = question.lower()
    for pat, sql in RULES:
        m = re.search(pat, q)
        if m:
            if sql is None:
                n = int(m.group(1))
                return f"SELECT p.name, SUM(oi.quantity) AS units FROM order_items oi JOIN products p USING(product_id) GROUP BY p.product_id ORDER BY units DESC LIMIT {n}"
            return sql
    raise ValueError("Fallback cannot answer this; set ANTHROPIC_API_KEY for full natural-language support")

def answer(question: str, db: str = "../sales-analytics-sql-python/retail.db"):
    sql = llm_sql(question) if os.environ.get("ANTHROPIC_API_KEY") else rule_sql(question)
    sql = validate_sql(sql)
    with sqlite3.connect(db) as conn:
        cur = conn.execute(sql)
        return sql, [d[0] for d in cur.description], cur.fetchall()

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "revenue by category"
    sql, cols, rows = answer(question)
    print("SQL:", sql, "\n", cols)
    for r in rows[:10]:
        print(r)
