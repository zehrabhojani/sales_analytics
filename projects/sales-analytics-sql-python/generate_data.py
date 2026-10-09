"""Create a synthetic retail database (customers, products, orders) in SQLite."""
import random, sqlite3, datetime as dt

random.seed(42)
conn = sqlite3.connect("retail.db")
c = conn.cursor()
c.executescript("""
DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers;
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, name TEXT, region TEXT, signup_date TEXT);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id));
CREATE TABLE order_items(order_id INTEGER, product_id INTEGER, quantity INTEGER,
                    FOREIGN KEY(order_id) REFERENCES orders(order_id),
                    FOREIGN KEY(product_id) REFERENCES products(product_id));
""")
regions = ["North", "South", "East", "West"]
cats = {"Electronics": (40, 400), "Home": (10, 120), "Fashion": (15, 150), "Books": (5, 40)}
start = dt.date(2025, 1, 1)
for i in range(1, 501):
    c.execute("INSERT INTO customers VALUES(?,?,?,?)",
              (i, f"Customer {i}", random.choice(regions), str(start + dt.timedelta(days=random.randint(0, 200)))))
pid = 1
for cat, (lo, hi) in cats.items():
    for k in range(1, 11):
        c.execute("INSERT INTO products VALUES(?,?,?,?)", (pid, f"{cat} item {k}", cat, round(random.uniform(lo, hi), 2)))
        pid += 1
for oid in range(1, 4001):
    cust = random.randint(1, 500)
    d = start + dt.timedelta(days=random.randint(0, 540))
    c.execute("INSERT INTO orders VALUES(?,?,?)", (oid, cust, str(d)))
    for p in random.sample(range(1, 41), random.randint(1, 4)):
        c.execute("INSERT INTO order_items VALUES(?,?,?)", (oid, p, random.randint(1, 3)))
conn.commit(); conn.close()
print("retail.db created")
