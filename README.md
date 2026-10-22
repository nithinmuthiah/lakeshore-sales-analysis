# Lakeshore Provisions Co. Sales Performance Analysis | Power BI + SQL

An end-to-end business analysis of a Midwest foodservice distributor: data cleaning, SQL analysis, a star-schema data model, and a 4-page Power BI dashboard that answers why growth slowed in one region and where the company is leaking revenue.

> **Data note:** Lakeshore Provisions is a fictional company. The dataset is synthetic, generated with Python (`scripts/generate_data.py`) to mimic real distributor sales patterns, including seasonality, customer concentration, and realistic data-quality problems.

---

## Business scenario

Lakeshore Provisions distributes food and supplies to restaurants, hospitals, schools, hotels, and caterers across five Midwest regions. Leadership asked for a review of the fiscal year that just closed (FY26: Oct 2025 – Sep 2026) to answer four questions:

1. How did we perform against last year and against plan?
2. Why is Northwest Indiana declining when other regions are growing?
3. Are our sales quotas fair, and which reps need support?
4. Where are we losing revenue we could recover?

## Key findings

| # | Finding | Evidence |
|---|---|---|
| 1 | **Revenue grew 6.2% to $6.15M**, and gross margin improved from 23.9% to 26.6% after the October 2025 list-price increase. | SQL Q1, Executive page |
| 2 | **Northwest Indiana fell 17.4%** because of a single account. Calumet Regional Health System was one-third of the region's revenue and stopped ordering after March 2026. Excluding it, the region grew 2.4%. | SQL Q3–Q4 |
| 3 | **Customer concentration risk:** the top 10% of customers generate 38% of revenue. Excluding Calumet, company growth would have been 11.2%. | SQL Q11 |
| 4 | **Quota problem, not a rep problem:** Tom Kowalski finished at 72% of quota, but his book outside Calumet grew 4%. His FY26 target was built assuming Calumet would keep ordering. | SQL Q6, Sales Team page |
| 5 | **Atlantic Salmon return rate jumped from 2.1% to 16.2%** starting June 2025 (other products average 2.1%), costing about $68K in returned revenue. This points to a supplier or cold-chain issue with Great Lakes Seafood Supply. | SQL Q7–Q8 |
| 6 | **The January 2026 dairy price increase backfired:** average price rose 12%, but units fell 21% and dairy revenue fell 11% (Jan–Sep, year over year). | SQL Q9, Product page |
| 7 | **Michigan West is the growth story** at +42.5%, the fastest-growing region. | SQL Q3 |
| 8 | **Eight high-value customers are at risk:** they each spent more than $10K in FY25 and haven't ordered in 90+ days, representing $504K of prior-year revenue. | SQL Q5, Customers page |

## Recommendations

1. **Run a win-back plan for Calumet Regional Health** and the other at-risk accounts, and add a 60-day no-order alert to the CRM.
2. **Reset the Northwest Indiana quota** to exclude lost accounts mid-year. Evaluate reps on retained-book growth, not only total attainment.
3. **Open a quality review with Great Lakes Seafood Supply**, and consider a second salmon supplier.
4. **Reverse or segment the dairy price increase:** the volume loss exceeded the price gain. Test the increase only on low-sensitivity segments.
5. **Invest in Michigan West** with additional rep capacity, since growth there is outpacing coverage.

---

## Repository structure

```
data/                    Raw CSV exports (intentionally messy)
  fact_order_lines.csv     ~34K order lines, Oct 2024 – Sep 2026
  fact_sales_targets.csv   Monthly revenue quota per rep
  dim_customers.csv        420 customers
  dim_products.csv         52 products, 8 categories
  dim_sales_reps.csv       12 reps
  dim_regions.csv          5 regions
sql/
  load_sqlite.py           Loads CSVs into lakeshore.db
  01_build_and_clean.sql   Data profiling + cleaned views
  02_business_questions.sql 13 business queries (CTEs, window functions)
powerbi/
  Lakeshore_Sales.pbix     Power BI report
  Lakeshore_Sales.pdf      PDF export of all pages
  dax_measures.md          All 34 DAX measures
  screenshots/             One image per report page
scripts/
  generate_data.py         Synthetic data generator
```

## Data model (star schema)

```
                 dim_date
                    │ Date
                    │
dim_customers ── fact_order_lines ── dim_products
  │ region_id          │ rep_id
  │                    │
dim_regions       dim_sales_reps ── fact_sales_targets ── dim_date
```

- `fact_order_lines[order_date]` → `dim_date[Date]` (many-to-one)
- `fact_order_lines[customer_id]` → `dim_customers[customer_id]`
- `fact_order_lines[product_id]` → `dim_products[product_id]`
- `fact_order_lines[rep_id]` → `dim_sales_reps[rep_id]`
- `dim_customers[region_id]` → `dim_regions[region_id]`
- `fact_sales_targets[rep_id]` → `dim_sales_reps[rep_id]`
- `fact_sales_targets[month_start]` → `dim_date[Date]`

All relationships are single-direction (dimension filters fact).

## Data quality issues found and fixed

| Issue | Count | Fix |
|---|---|---|
| Exact duplicate order lines | 136 | Removed duplicates on `order_id` + `line_number` |
| Inconsistent status values (`DELIVERED`, `delivered`, padded spaces) | 341 | Trimmed and set to Proper Case |
| Order lines with no sales rep | 204 | Filled from the customer's account owner |
| Zero-quantity lines (data entry errors) | 25 | Removed |
| Abbreviated segment names (`Indep. Restaurant`, `Rest. Group`) | 7 | Mapped to standard names |
| ALL-CAPS city names, trailing spaces in customer names | 34 | Trimmed and set to Proper Case |

---

## Dashboard

Four report pages plus a hidden drill-through page. Each page title states the finding it supports.

### 1. Executive Summary
![Executive Summary](powerbi/screenshots/1-executive-summary.png)

- Fiscal Year slicer (FY26 selected)
- KPI card: Revenue, Revenue YoY %, Gross Margin %, Orders, Avg Order Value, Quota Attainment %
- Line chart: Revenue vs. prior year by month
- Bar chart: Revenue YoY % by region, red for decline and green for growth

### 2. Regions and Customers
![Regions and Customers](powerbi/screenshots/2-regions-customers.png)

- Waterfall chart: Northwest Indiana revenue, FY25 to FY26, broken down by customer. The single large red step is Calumet Regional Health System (-$241K).
- At-risk table: 8 customers with more than $10K in FY25 revenue and no order in 90+ days, filtered with the `At-Risk Customers` measure
- Bar chart: top 20 customers by revenue, showing concentration risk

### 3. Sales Team
![Sales Team](powerbi/screenshots/3-sales-team.png)

- Bar chart: quota attainment by rep, colored by the `Attainment Color` measure (green at 100%+, yellow at 90–99%, red below 90%), with a 100% target line
- **Drill-through:** right-click any rep and choose Drill through → Rep Detail to see their customers' revenue vs. prior year. For Tom Kowalski, it shows the entire shortfall is Calumet: his other accounts grew from $530,876 to $552,423 (+4%).

### 4. Products & Pricing
![Products & Pricing](powerbi/screenshots/4-products-pricing.png)

- Bar chart: top 10 products by return rate. Atlantic Salmon is at about 11%, against 2–4% for everything else.
- Line chart: Atlantic Salmon return rate by month, jumping from June 2025
- Combo chart (Dairy only): units sold (columns) vs. average net price (line). Price spikes in January 2026 and volume drops.

## How it was built

1. **Power Query:** loaded the six CSVs and fixed every issue in the data-quality table above (trim and proper case, duplicates removed, zero quantities filtered, missing reps filled through a merge with `dim_customers`, segment names standardized, `dim_regions` headers promoted).
2. **Model:** built a `dim_date` table with an October–September fiscal calendar, marked it as the date table, and created the 7 single-direction relationships above.
3. **Measures:** added 34 DAX measures in a dedicated `Key Measures` table through DAX query view (see `powerbi/dax_measures.md`), including time intelligence, quota attainment, return rate, at-risk customers, and conditional-format color logic.
4. **Report:** four pages and one hidden drill-through page, with conditional formatting, Top N filters, and synced Fiscal Year slicers.

---

## Skills demonstrated

SQL (CTEs, window functions, joins, data profiling) · Power Query data cleaning · Star-schema data modeling · DAX (time intelligence, CALCULATE, RANKX, TOPN, drill-through, conditional formatting) · KPI design · Root-cause analysis · Business recommendations

## Reproduce

```bash
python scripts/generate_data.py   # optional: regenerate data/
python sql/load_sqlite.py         # build lakeshore.db
# then run sql/02_business_questions.sql in DB Browser for SQLite or VS Code
```
