# ETL Data Pipeline (cloud-ready)

Python ETL that extracts raw order CSV data, validates and cleans it (types, dates, nulls, duplicates),
loads good rows into a SQL table and reports rejected rows with reasons. Unit tested.
`lambda_handler` uses the AWS Lambda signature, so it can be attached to an S3 upload event;
cloud deployment is a planned next step and is not included.

```
python etl_pipeline.py
python -m unittest
```
