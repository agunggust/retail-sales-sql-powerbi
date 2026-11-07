# Power BI dashboard build guide

## Import

1. Open Power BI Desktop.
2. Select **Get data > Excel workbook**.
3. Choose `Retail_Sales_Analytics_Source.xlsx`.
4. Import the `Sales`, `Products`, `Customers`, and `Calendar` sheets or their
   corresponding named tables. Use the model table names `SalesTable`,
   `ProductsTable`, `CustomersTable`, and `CalendarTable`.
5. In Power Query, confirm that IDs and labels are Text, quantities are Whole Number,
   amounts are Decimal Number, and dates are Date. Select **Close & Apply**.

## Data model

Create these one-to-many, single-direction relationships:

- `CalendarTable[date]` -> `SalesTable[order_date]`
- `ProductsTable[product_id]` -> `SalesTable[product_id]`
- `CustomersTable[customer_id]` -> `SalesTable[customer_id]`

Mark `CalendarTable` as the date table using its `date` column. Sort `CalendarTable[month_name]`
by `CalendarTable[month_number]`.

## Measures

Copy the measures from `DAX_Measures.txt`. Format revenue, profit, and average order
value as Indonesian Rupiah with zero decimals. Format margins and growth as percentages.

Use `CalendarTable[year_month]` on the rows of a visual with Revenue MoM %. The
measure compares full calendar months. A partial month or a total across
multiple months is blank.

In the included PBIX, open **Monthly Revenue** and select January and March
in the month slicer. January should be blank because December 2024 is outside
the dataset. March should show **23.45%** against February's Rp54,591,550, and
the combined total should be blank. Clear the slicer to see all months again.

Open DAX Query View and run the saved query to repeat the filter checks,
including a partial March selection and the full-year total. Both should
return a blank MoM value.

## One-page layout

Use a 16:9 page with a white background and a dark-blue title. Add:

1. Four cards: Total Revenue, Total Profit, Profit Margin, Total Orders.
2. Line chart: `CalendarTable[year_month]` and `[Total Revenue]`.
3. Bar chart: `ProductsTable[category]` and `[Total Profit]`, sorted descending.
4. Column chart: `SalesTable[channel]` and `[Total Revenue]`.
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

