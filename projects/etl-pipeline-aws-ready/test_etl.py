import unittest
from etl_pipeline import transform, extract

CSV = "order_id,customer,order_date,quantity,unit_price\n1,a b,2026-01-01,2,5\n1,a b,2026-01-01,2,5\n2,,2026-01-01,1,5\n3,c d,bad,1,5\n"

class TestETL(unittest.TestCase):
    def test_clean_reject_split(self):
        clean, rej = transform(extract(CSV))
        self.assertEqual(len(clean), 1)
        self.assertEqual(clean[0]["total"], 10.0)
        self.assertEqual({r["reason"].split(":")[0] for r in rej}, {"duplicate order_id", "missing customer", "invalid field"})

if __name__ == "__main__":
    unittest.main()
