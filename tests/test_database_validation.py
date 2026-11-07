import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import generate_data


class DatabaseValidationTests(unittest.TestCase):
    def setUp(self):
        temp_dir = self.enterContext(TemporaryDirectory())
        self.db_path = Path(temp_dir) / "retail.db"
        self.enterContext(patch.object(generate_data, "DB_PATH", self.db_path))
        self.data = generate_data.build_data()

    def test_rejects_missing_sales_rows(self):
        generate_data.create_database(self.data)
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("DELETE FROM fact_sales WHERE sale_id = 'S000001'")
            with self.assertRaisesRegex(ValueError, "fact rows: source 1513, database 1512"):
                generate_data.validate_database(connection, self.data["sales"])

    def test_revenue_mismatch_preserves_existing_database(self):
        generate_data.create_database(self.data)
        previous_db = self.db_path.read_bytes()
        validate_database = generate_data.validate_database

        def validate_changed_revenue(connection, sales):
            connection.execute("UPDATE fact_sales SET revenue = revenue + 1 WHERE sale_id = 'S000001'")
            return validate_database(connection, sales)

        with patch.object(generate_data, "validate_database", validate_changed_revenue):
            with self.assertRaisesRegex(ValueError, r"revenue: .*difference \+1\.00"):
                generate_data.create_database(self.data)

        self.assertEqual(self.db_path.read_bytes(), previous_db)
