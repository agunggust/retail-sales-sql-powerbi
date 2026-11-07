"""Generate deterministic synthetic retail data, SQLite DB, and query outputs."""

from __future__ import annotations

import csv
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUERY_DIR = ROOT / "query_outputs"
DB_PATH = ROOT / "retail_sales.db"
SCHEMA_PATH = ROOT / "sql" / "01_schema.sql"
SUMMARY_PATH = ROOT / "project_summary.json"
SEED = 20261105

PRODUCTS = [
    ("Wireless Earbuds", "Electronics", "Audio", 260_000, 499_000),
    ("Smart Watch", "Electronics", "Wearables", 540_000, 899_000),
    ("Mechanical Keyboard", "Electronics", "Computer Accessories", 420_000, 749_000),
    ("Portable Speaker", "Electronics", "Audio", 320_000, 599_000),
    ("Desk Lamp", "Home", "Lighting", 115_000, 229_000),
    ("Storage Organizer", "Home", "Storage", 80_000, 169_000),
    ("Coffee Grinder", "Home", "Kitchen", 275_000, 499_000),
    ("Vacuum Flask", "Home", "Kitchen", 95_000, 199_000),
    ("Running Shoes", "Fashion", "Footwear", 380_000, 699_000),
    ("Casual Backpack", "Fashion", "Bags", 210_000, 399_000),
    ("Basic T-Shirt", "Fashion", "Apparel", 72_000, 149_000),
    ("Light Jacket", "Fashion", "Apparel", 230_000, 459_000),
    ("Yoga Mat", "Sports", "Fitness", 125_000, 249_000),
    ("Resistance Bands", "Sports", "Fitness", 65_000, 139_000),
    ("Badminton Racket", "Sports", "Racket Sports", 290_000, 549_000),
    ("Insulated Bottle", "Sports", "Outdoor", 105_000, 219_000),
    ("Facial Cleanser", "Beauty", "Skincare", 58_000, 119_000),
    ("Sunscreen SPF 50", "Beauty", "Skincare", 72_000, 149_000),
    ("Hair Dryer", "Beauty", "Personal Care", 240_000, 449_000),
    ("Grooming Kit", "Beauty", "Personal Care", 195_000, 379_000),
]

CITIES = ["Jakarta", "Bandung", "Surabaya", "Medan", "Yogyakarta"]
CITY_WEIGHTS = [0.36, 0.23, 0.18, 0.12, 0.11]
SEGMENTS = ["Consumer", "Small Business", "VIP"]
SEGMENT_WEIGHTS = [0.68, 0.23, 0.09]
CHANNELS = ["Marketplace", "Website", "Retail Store"]
CHANNEL_WEIGHTS = [0.46, 0.34, 0.20]
MONTH_WEIGHTS = [0.78, 0.82, 0.94, 1.02, 0.96, 1.00, 1.05, 1.08, 1.00, 1.12, 1.38, 1.55]


def write_csv(path: Path, headers: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def choose_order_date(rng: random.Random) -> date:
    month = rng.choices(range(1, 13), weights=MONTH_WEIGHTS, k=1)[0]
    first = date(2025, month, 1)
    next_month = date(2026, 1, 1) if month == 12 else date(2025, month + 1, 1)
    return first + timedelta(days=rng.randrange((next_month - first).days))


def build_data() -> dict[str, list[tuple]]:
    rng = random.Random(SEED)

    calendar = []
    current = date(2025, 1, 1)
    while current <= date(2025, 12, 31):
        calendar.append(
            (
                current.isoformat(), current.year, f"Q{((current.month - 1) // 3) + 1}",
                current.month, current.strftime("%B"), current.strftime("%Y-%m"),
                current.isocalendar().week, current.strftime("%A"),
            )
        )
        current += timedelta(days=1)

    products = [
        (f"P{index:03d}", name, category, subcategory, cost, price)
        for index, (name, category, subcategory, cost, price) in enumerate(PRODUCTS, 1)
    ]

    customers = []
    for index in range(1, 251):
        city = rng.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
        segment = rng.choices(SEGMENTS, weights=SEGMENT_WEIGHTS, k=1)[0]
        joined = date(2024, 1, 1) + timedelta(days=rng.randrange(365))
        customers.append((f"C{index:04d}", city, segment, joined.isoformat()))

    product_lookup = {row[0]: row for row in products}
    sales = []
    sale_number = 1
    for order_number in range(1, 901):
        order_id = f"O{order_number:05d}"
        order_date = choose_order_date(rng)
        customer_id = rng.choice(customers)[0]
        channel = rng.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0]
        item_count = rng.choices([1, 2, 3], weights=[0.48, 0.37, 0.15], k=1)[0]
        chosen_products = rng.sample([row[0] for row in products], item_count)

        for product_id in chosen_products:
            product = product_lookup[product_id]
            quantity = rng.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05], k=1)[0]
            discount_pool = [0.00, 0.05, 0.10, 0.15]
            discount_weights = [0.42, 0.31, 0.20, 0.07]
            if order_date.month in (11, 12):
                discount_pool.append(0.20)
                discount_weights = [0.25, 0.28, 0.25, 0.14, 0.08]
            discount_pct = rng.choices(discount_pool, weights=discount_weights, k=1)[0]
            unit_cost = product[4]
            unit_price = product[5]
            revenue = round(unit_price * quantity * (1 - discount_pct), 2)
            total_cost = round(unit_cost * quantity, 2)
            profit = round(revenue - total_cost, 2)
            sales.append(
                (
                    f"S{sale_number:06d}", order_id, order_date.isoformat(), customer_id,
                    product_id, channel, quantity, unit_price, discount_pct,
                    revenue, total_cost, profit,
                )
            )
            sale_number += 1

    return {"calendar": calendar, "products": products, "customers": customers, "sales": sales}


def validate_database(connection: sqlite3.Connection, sales: list[tuple]) -> dict:
    fact_rows, orders, database_revenue = connection.execute(
        "SELECT COUNT(*), COUNT(DISTINCT order_id), COALESCE(SUM(revenue), 0) FROM fact_sales"
    ).fetchone()
    source_revenue = round(sum(row[9] for row in sales), 2)
    checks = {
        "fact_rows": fact_rows,
        "orders": orders,
        "orphan_dates": connection.execute(
            "SELECT COUNT(*) FROM fact_sales s LEFT JOIN dim_date d "
            "ON d.date = s.order_date WHERE d.date IS NULL"
        ).fetchone()[0],
        "orphan_products": connection.execute(
            "SELECT COUNT(*) FROM fact_sales s LEFT JOIN dim_product p "
            "ON p.product_id = s.product_id WHERE p.product_id IS NULL"
        ).fetchone()[0],
        "orphan_customers": connection.execute(
            "SELECT COUNT(*) FROM fact_sales s LEFT JOIN dim_customer c "
            "ON c.customer_id = s.customer_id WHERE c.customer_id IS NULL"
        ).fetchone()[0],
        "negative_profit_rows": connection.execute(
            "SELECT COUNT(*) FROM fact_sales WHERE profit < 0"
        ).fetchone()[0],
        "revenue_reconciliation": round(database_revenue - source_revenue, 2),
    }

    errors = []
    if fact_rows != len(sales):
        errors.append(f"fact rows: source {len(sales)}, database {fact_rows}")
    if checks["revenue_reconciliation"]:
        errors.append(
            f"revenue: source {source_revenue:.2f}, database {database_revenue:.2f}, "
            f"difference {checks['revenue_reconciliation']:+.2f}"
        )
    for name in ("orphan_dates", "orphan_products", "orphan_customers", "negative_profit_rows"):
        if checks[name]:
            errors.append(f"{name}: {checks[name]}")
    if errors:
        raise ValueError("Database validation failed: " + ", ".join(errors))
    return checks


def create_database(data: dict[str, list[tuple]]) -> dict:
    with TemporaryDirectory(dir=DB_PATH.parent) as temp_dir:
        temp_db = Path(temp_dir) / DB_PATH.name
        connection = sqlite3.connect(temp_db)
        try:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            connection.executemany("INSERT INTO dim_date VALUES (?,?,?,?,?,?,?,?)", data["calendar"])
            connection.executemany("INSERT INTO dim_product VALUES (?,?,?,?,?,?)", data["products"])
            connection.executemany("INSERT INTO dim_customer VALUES (?,?,?,?)", data["customers"])
            connection.executemany("INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", data["sales"])
            checks = validate_database(connection, data["sales"])
            connection.commit()
        finally:
            connection.close()
        temp_db.replace(DB_PATH)
    return checks


def query_to_csv(connection: sqlite3.Connection, filename: str, query: str) -> list[tuple]:
    cursor = connection.execute(query)
    rows = cursor.fetchall()
    write_csv(QUERY_DIR / filename, [item[0] for item in cursor.description], rows)
    return rows


def create_query_outputs() -> dict:
    QUERY_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    try:
        kpi = query_to_csv(connection, "kpi_summary.csv", """
            SELECT ROUND(SUM(revenue),0), ROUND(SUM(profit),0),
                   ROUND(100.0*SUM(profit)/SUM(revenue),2), COUNT(DISTINCT order_id),
                   ROUND(SUM(revenue)/COUNT(DISTINCT order_id),0), COUNT(DISTINCT customer_id)
            FROM fact_sales
        """)[0]
        monthly = query_to_csv(connection, "monthly_performance.csv", """
            WITH m AS (
              SELECT d.year_month, COALESCE(SUM(s.revenue), 0) revenue,
                     COALESCE(SUM(s.profit), 0) profit,
                     COUNT(DISTINCT s.order_id) orders
              FROM dim_date d LEFT JOIN fact_sales s ON s.order_date=d.date GROUP BY d.year_month
            ), p AS (
              SELECT *, LAG(revenue) OVER (ORDER BY year_month) previous_revenue FROM m
            )
            SELECT year_month, ROUND(revenue,0), ROUND(profit,0), orders,
                   ROUND(100.0*profit/revenue,2),
                   ROUND(100.0*(revenue-previous_revenue)/previous_revenue,2)
            FROM p ORDER BY year_month
        """)
        category = query_to_csv(connection, "category_performance.csv", """
            SELECT p.category, ROUND(SUM(s.revenue),0), ROUND(SUM(s.profit),0),
                   ROUND(100.0*SUM(s.profit)/SUM(s.revenue),2), SUM(s.quantity)
            FROM fact_sales s JOIN dim_product p ON p.product_id=s.product_id
            GROUP BY p.category ORDER BY SUM(s.revenue) DESC
        """)
        channel = query_to_csv(connection, "channel_performance.csv", """
            SELECT channel, ROUND(SUM(revenue),0), ROUND(SUM(profit),0),
                   COUNT(DISTINCT order_id), ROUND(SUM(revenue)/COUNT(DISTINCT order_id),0)
            FROM fact_sales GROUP BY channel ORDER BY SUM(revenue) DESC
        """)
        top_products = query_to_csv(connection, "top_products.csv", """
            SELECT p.product_name, p.category, ROUND(SUM(s.revenue),0),
                   ROUND(SUM(s.profit),0), SUM(s.quantity)
            FROM fact_sales s JOIN dim_product p ON p.product_id=s.product_id
            GROUP BY p.product_id ORDER BY SUM(s.revenue) DESC LIMIT 10
        """)

    finally:
        connection.close()

    return {
        "kpi": kpi,
        "monthly": monthly,
        "category": category,
        "channel": channel,
        "top_products": top_products,
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = build_data()
    checks = create_database(data)
    write_csv(DATA_DIR / "calendar.csv", ["date", "year", "quarter", "month_number", "month_name", "year_month", "week_number", "day_name"], data["calendar"])
    write_csv(DATA_DIR / "products.csv", ["product_id", "product_name", "category", "subcategory", "unit_cost", "list_price"], data["products"])
    write_csv(DATA_DIR / "customers.csv", ["customer_id", "city", "customer_segment", "join_date"], data["customers"])
    write_csv(DATA_DIR / "sales.csv", ["sale_id", "order_id", "order_date", "customer_id", "product_id", "channel", "quantity", "unit_price", "discount_pct", "revenue", "total_cost", "profit"], data["sales"])
    analysis = create_query_outputs()
    summary = {
        "seed": SEED,
        "synthetic": True,
        "rows": {key: len(value) for key, value in data.items()},
        **analysis,
        "checks": checks,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["checks"], indent=2))


if __name__ == "__main__":
    main()

