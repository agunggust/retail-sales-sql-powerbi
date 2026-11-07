import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

from scripts.generate_data import read_analysis_queries


ROOT = Path(__file__).resolve().parents[1]


class MonthlyPerformanceTests(unittest.TestCase):
    def test_month_without_sales_preserves_calendar_comparison(self):
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                (ROOT / "sql" / "01_schema.sql").read_text(encoding="utf-8")
            )
            connection.executemany(
                "INSERT INTO dim_date VALUES (?, 2025, 'Q1', ?, ?, ?, 1, 'Day')",
                [
                    ("2025-01-01", 1, "January", "2025-01"),
                    ("2025-02-01", 2, "February", "2025-02"),
                    ("2025-03-01", 3, "March", "2025-03"),
                ],
            )
            connection.execute("INSERT INTO dim_product VALUES ('P', 'Product', 'C', 'S', 50, 100)")
            connection.execute("INSERT INTO dim_customer VALUES ('C', 'City', 'Segment', '2024-01-01')")
            connection.executemany(
                "INSERT INTO fact_sales VALUES (?, ?, ?, 'C', 'P', 'Web', 1, 100, 0, 100, 50, 50)",
                [("S1", "O1", "2025-01-01"), ("S2", "O2", "2025-03-01")],
            )

            monthly_query = read_analysis_queries()["monthly_performance"]
            rows = connection.execute(monthly_query).fetchall()

        self.assertEqual(rows, [
            ("2025-01", 100, 50, 1, 50, None),
            ("2025-02", 0, 0, 0, None, -100),
            ("2025-03", 100, 50, 1, 50, None),
        ])
