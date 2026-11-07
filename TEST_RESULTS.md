# Validation results

Generated with deterministic seed `20261105`.

- Sales fact rows: 1,513
- Distinct orders: 900
- Products: 20
- Customers: 250; active customers: 242
- Calendar dates: 365
- Total revenue: Rp944,480,400
- Total profit: Rp413,325,400
- Profit margin: 43.76%
- Average order value: Rp1,049,423
- Orphan date keys: 0
- Orphan product keys: 0
- Orphan customer keys: 0
- Negative-profit rows: 0
- Source-to-database revenue difference: Rp0
- Workbook formula-error scan: 0 matches

The workbook was rendered and visually checked for the dashboard, source tables,
calendar, and Power BI checklist. The dataset is synthetic.

## Power BI Desktop checks

- The **Monthly Revenue** slicer shows January and March when selected
  together. January and the combined total have blank MoM values, and March
  shows 23.45% growth over February.
- The saved DAX Query View query evaluates the model measures under full-month,
  noncontiguous, partial-month, and full-year filters. March uses February
  revenue of Rp54,591,550. January, the combined selection, March 1-15, and the
  full-year total have blank MoM values.
- The unfiltered model revenue matches SQLite at Rp944,480,400.
