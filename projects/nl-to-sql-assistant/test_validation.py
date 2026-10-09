import unittest
from nl_to_sql import validate_sql

class TestValidation(unittest.TestCase):
    def test_select_ok(self):
        self.assertTrue(validate_sql("SELECT * FROM customers;").startswith("SELECT"))
    def test_with_ok(self):
        validate_sql("WITH a AS (SELECT 1) SELECT * FROM a")
    def test_drop_blocked(self):
        with self.assertRaises(ValueError): validate_sql("DROP TABLE customers")
    def test_stacked_blocked(self):
        with self.assertRaises(ValueError): validate_sql("SELECT 1; DELETE FROM orders")
    def test_update_in_select_blocked(self):
        with self.assertRaises(ValueError): validate_sql("SELECT * FROM t WHERE 1=1 OR update=1")

if __name__ == "__main__":
    unittest.main()
