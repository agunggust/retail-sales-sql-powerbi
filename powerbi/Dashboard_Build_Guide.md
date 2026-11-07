# Power BI dashboard build guide

## Import

1. Open Power BI Desktop.
2. Select **Get data > Excel workbook**.
3. Choose `Retail_Sales_Analytics_Source.xlsx`.
4. Import these sheets: `Sales`, `Products`, `Customers`, and `Calendar`.
5. In Power Query, confirm that IDs and labels are Text, quantities are Whole Number,
   amounts are Decimal Number, and dates are Date. Select **Close & Apply**.

## Data model

Create these one-to-many, single-direction relationships:

- `Calendar[date]` -> `Sales[order_date]`
- `Products[product_id]` -> `Sales[product_id]`
- `Customers[customer_id]` -> `Sales[customer_id]`

Mark `Calendar` as the date table using its `date` column. Sort `Calendar[month_name]`
by `Calendar[month_number]`.

## Measures

Copy the measures from `DAX_Measures.txt`. Format revenue, profit, and average order
value as Indonesian Rupiah with zero decimals. Format margins and growth as percentages.

Use `Calendar[year_month]` on the rows of a visual with Revenue MoM %. The
measure compares full calendar months. A partial month or a total across
multiple months is blank.

To check the measure in Power BI Desktop, add it to a table by year and month.
January 2025 should be blank because December 2024 is outside the dataset.
Select January and March together in a slicer. January should remain blank,
March should compare with February, and the combined total should be blank.
Select only part of March and confirm the result is blank.

## One-page layout

Use a 16:9 page with a white background and a dark-blue title. Add:

1. Four cards: Total Revenue, Total Profit, Profit Margin, Total Orders.
2. Line chart: `Calendar[year_month]` and `[Total Revenue]`.
3. Bar chart: `Products[category]` and `[Total Profit]`, sorted descending.
4. Column chart: `Sales[channel]` and `[Total Revenue]`.
5. Table: product name, category, Total Revenue, Total Profit, Units Sold.
6. Slicers: Calendar date, Customers city, Sales channel.

Recommended colors: navy `#17324D`, teal `#22A699`, orange `#F4A261`,
light gray `#EEF2F5`. Keep all currency axes in IDR millions.

## Questions the dashboard answers

- How did revenue change month by month?
- Which categories and products generate the most revenue and profit?
- Which channel has the highest order value?
- Which cities and customer segments contribute the most revenue?
- Are higher sales accompanied by healthy profit margins?

