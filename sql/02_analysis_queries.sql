-- 1. Executive KPI summary
SELECT
    ROUND(SUM(revenue), 0) AS total_revenue,
    ROUND(SUM(profit), 0) AS total_profit,
    ROUND(100.0 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 0) AS average_order_value,
    COUNT(DISTINCT customer_id) AS active_customers
FROM fact_sales;

-- 2. Monthly trend with month-over-month growth
WITH monthly AS (
    SELECT
        d.year_month,
        SUM(s.revenue) AS revenue,
        SUM(s.profit) AS profit,
        COUNT(DISTINCT s.order_id) AS orders
    FROM fact_sales s
    JOIN dim_date d ON d.date = s.order_date
    GROUP BY d.year_month
), with_previous AS (
    SELECT
        *,
        LAG(revenue) OVER (ORDER BY year_month) AS previous_month_revenue
    FROM monthly
)
SELECT
    year_month,
    ROUND(revenue, 0) AS revenue,
    ROUND(profit, 0) AS profit,
    orders,
    ROUND(100.0 * profit / NULLIF(revenue, 0), 2) AS profit_margin_pct,
    ROUND(100.0 * (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0), 2) AS revenue_mom_pct
FROM with_previous
ORDER BY year_month;

-- 3. Category performance
SELECT
    p.category,
    ROUND(SUM(s.revenue), 0) AS revenue,
    ROUND(SUM(s.profit), 0) AS profit,
    ROUND(100.0 * SUM(s.profit) / NULLIF(SUM(s.revenue), 0), 2) AS profit_margin_pct,
    SUM(s.quantity) AS units_sold
FROM fact_sales s
JOIN dim_product p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 4. Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(s.revenue), 0) AS revenue,
    ROUND(SUM(s.profit), 0) AS profit,
    SUM(s.quantity) AS units_sold,
    DENSE_RANK() OVER (ORDER BY SUM(s.revenue) DESC) AS revenue_rank
FROM fact_sales s
JOIN dim_product p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 5. Sales channel performance
SELECT
    channel,
    ROUND(SUM(revenue), 0) AS revenue,
    ROUND(SUM(profit), 0) AS profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 0) AS average_order_value
FROM fact_sales
GROUP BY channel
ORDER BY revenue DESC;

-- 6. Customer segment performance
SELECT
    c.customer_segment,
    COUNT(DISTINCT s.customer_id) AS active_customers,
    COUNT(DISTINCT s.order_id) AS orders,
    ROUND(SUM(s.revenue), 0) AS revenue,
    ROUND(SUM(s.revenue) / COUNT(DISTINCT s.customer_id), 0) AS revenue_per_customer
FROM fact_sales s
JOIN dim_customer c ON c.customer_id = s.customer_id
GROUP BY c.customer_segment
ORDER BY revenue DESC;

-- 7. City performance
SELECT
    c.city,
    COUNT(DISTINCT s.order_id) AS orders,
    ROUND(SUM(s.revenue), 0) AS revenue,
    ROUND(SUM(s.profit), 0) AS profit
FROM fact_sales s
JOIN dim_customer c ON c.customer_id = s.customer_id
GROUP BY c.city
ORDER BY revenue DESC;

