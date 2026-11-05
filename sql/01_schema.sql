PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    month_number INTEGER NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    month_name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    day_name TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
    list_price REAL NOT NULL CHECK (list_price >= unit_cost)
);

CREATE TABLE dim_customer (
    customer_id TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    join_date TEXT NOT NULL
);

CREATE TABLE fact_sales (
    sale_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_date TEXT NOT NULL REFERENCES dim_date(date),
    customer_id TEXT NOT NULL REFERENCES dim_customer(customer_id),
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    channel TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_pct REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 1),
    revenue REAL NOT NULL CHECK (revenue >= 0),
    total_cost REAL NOT NULL CHECK (total_cost >= 0),
    profit REAL NOT NULL
);

CREATE INDEX idx_sales_date ON fact_sales(order_date);
CREATE INDEX idx_sales_product ON fact_sales(product_id);
CREATE INDEX idx_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_sales_order ON fact_sales(order_id);

