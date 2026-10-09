"""Run the SQL queries, print results, save CSVs and a revenue chart."""
import re, sqlite3, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

conn = sqlite3.connect("retail.db")
sql = open("queries.sql").read()
queries = dict(re.findall(r"-- name: (\w+)\n(.*?)(?=\n-- name:|\Z)", sql, re.S))
results = {}
for name, q in queries.items():
    results[name] = pd.read_sql_query(q, conn)
    results[name].to_csv(f"{name}.csv", index=False)
    print(f"\n== {name} ==\n{results[name].head(8).to_string(index=False)}")

m = results["monthly_revenue_running_total"]
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(m["month"], m["revenue"], color="#1F2A44")
ax.set_title("Monthly revenue"); ax.set_ylabel("Revenue"); plt.xticks(rotation=60)
plt.tight_layout(); plt.savefig("monthly_revenue.png", dpi=120)
print("\nSaved CSVs and monthly_revenue.png")
