# Natural-Language-to-SQL Assistant

Ask business questions in English and get SQL plus results from the retail database
(build it first in `../sales-analytics-sql-python`). With `ANTHROPIC_API_KEY` set it uses an LLM
(SQL generation with schema context); without a key a small rule-based fallback runs offline.
Safety: only single read-only SELECT/WITH statements are executed; tests in `test_validation.py`.

```
python nl_to_sql.py "revenue by category"
python nl_to_sql.py "top 5 products"
python -m unittest
```
