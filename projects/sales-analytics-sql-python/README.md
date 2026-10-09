# Retail Sales Analytics (SQL + Python)

Relational model (customers, products, orders, order_items) in SQLite with analytical SQL:
joins, CTEs, window functions (running totals, RANK) and a repeat-customer metric.
Python (pandas, matplotlib) runs the queries, exports CSVs and plots monthly revenue.

```
python generate_data.py   # builds retail.db with synthetic data
python analysis.py        # runs queries.sql, writes CSVs + chart
```
Data is synthetic. Business questions answered: revenue by category, monthly trend, top customers per region, repeat rate.
