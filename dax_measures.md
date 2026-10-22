# DAX Measures

All measures live in a dedicated table named `Key Measures`. ("Measures" is a reserved name in Power BI, so a different name is needed.)

Table names below match the Power Query query names: `fact_order_lines`, `fact_sales_targets`, `dim_customers`, `dim_products`, `dim_sales_reps`, `dim_regions`, `dim_date`.

## Fastest way to add them: one paste in DAX query view

1. Create the measures table: Home → **New table** → `Key Measures = { 1 }`. Hide its `Value` column after the measures are added.
2. Open **DAX query view** (left bar), paste the block below, and click **Update model with changes**.
3. Set number formats afterward on the Measure tools ribbon.

```dax
DEFINE
    MEASURE 'Key Measures'[Revenue] = CALCULATE ( SUM ( fact_order_lines[Net Revenue] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Gross Profit] = [Revenue] - CALCULATE ( SUM ( fact_order_lines[COGS] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Gross Margin %] = DIVIDE ( [Gross Profit], [Revenue] )
    MEASURE 'Key Measures'[Orders] = CALCULATE ( DISTINCTCOUNT ( fact_order_lines[order_id] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Avg Order Value] = DIVIDE ( [Revenue], [Orders] )
    MEASURE 'Key Measures'[Units Sold] = CALCULATE ( SUM ( fact_order_lines[quantity] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Active Customers] = CALCULATE ( DISTINCTCOUNT ( fact_order_lines[customer_id] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Revenue PY] = CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( dim_date[Date] ) )
    MEASURE 'Key Measures'[Revenue YoY %] = DIVIDE ( [Revenue] - [Revenue PY], [Revenue PY] )
    MEASURE 'Key Measures'[Revenue FYTD] = TOTALYTD ( [Revenue], dim_date[Date], "9/30" )
    MEASURE 'Key Measures'[Revenue PM] = CALCULATE ( [Revenue], DATEADD ( dim_date[Date], -1, MONTH ) )
    MEASURE 'Key Measures'[Revenue MoM %] = DIVIDE ( [Revenue] - [Revenue PM], [Revenue PM] )
    MEASURE 'Key Measures'[Revenue Rolling 3M] = CALCULATE ( [Revenue], DATESINPERIOD ( dim_date[Date], MAX ( dim_date[Date] ), -3, MONTH ) )
    MEASURE 'Key Measures'[Revenue Running Total] = CALCULATE ( [Revenue], FILTER ( ALLSELECTED ( dim_date[Date] ), dim_date[Date] <= MAX ( dim_date[Date] ) ) )
    MEASURE 'Key Measures'[Target] = SUM ( fact_sales_targets[revenue_target] )
    MEASURE 'Key Measures'[Quota Attainment %] = DIVIDE ( [Revenue], [Target] )
    MEASURE 'Key Measures'[Variance to Target] = [Revenue] - [Target]
    MEASURE 'Key Measures'[Attainment Color] = SWITCH ( TRUE (), [Quota Attainment %] >= 1, "#2E7D32", [Quota Attainment %] >= 0.9, "#F9A825", "#C62828" )
    MEASURE 'Key Measures'[Months Hit Target] = SUMX ( VALUES ( dim_date[Month Start] ), IF ( [Revenue] >= [Target] && [Target] > 0, 1 ) )
    MEASURE 'Key Measures'[Returned Lines] = CALCULATE ( COUNTROWS ( fact_order_lines ), fact_order_lines[status] = "Returned" )
    MEASURE 'Key Measures'[Return Rate %] = DIVIDE ( [Returned Lines], CALCULATE ( COUNTROWS ( fact_order_lines ), fact_order_lines[status] <> "Cancelled" ) )
    MEASURE 'Key Measures'[Revenue Lost to Returns] = CALCULATE ( SUM ( fact_order_lines[Net Revenue] ), fact_order_lines[status] = "Returned" )
    MEASURE 'Key Measures'[Last Order Date] = CALCULATE ( MAX ( fact_order_lines[order_date] ), fact_order_lines[Is Revenue Line] = 1 )
    MEASURE 'Key Measures'[Days Since Last Order] = DATEDIFF ( [Last Order Date], DATE ( 2026, 9, 30 ), DAY )
    MEASURE 'Key Measures'[At-Risk Customers] = COUNTROWS ( FILTER ( VALUES ( dim_customers[customer_id] ), [Days Since Last Order] > 90 && CALCULATE ( [Revenue], dim_date[Fiscal Year] = "FY25" ) > 10000 ) )
    MEASURE 'Key Measures'[Customer Rank] = RANKX ( ALL ( dim_customers[customer_name] ), [Revenue], , DESC, DENSE )
    MEASURE 'Key Measures'[Top 10% Revenue Share] = DIVIDE ( CALCULATE ( [Revenue], TOPN ( ROUNDUP ( COUNTROWS ( ALL ( dim_customers ) ) * 0.1, 0 ), ALL ( dim_customers[customer_id] ), [Revenue], DESC ) ), CALCULATE ( [Revenue], ALL ( dim_customers ) ) )
    MEASURE 'Key Measures'[Avg Net Price per Unit] = DIVIDE ( [Revenue], [Units Sold] )
    MEASURE 'Key Measures'[Units PY] = CALCULATE ( [Units Sold], SAMEPERIODLASTYEAR ( dim_date[Date] ) )
    MEASURE 'Key Measures'[Units YoY %] = DIVIDE ( [Units Sold] - [Units PY], [Units PY] )
    MEASURE 'Key Measures'[Avg Price PY] = CALCULATE ( [Avg Net Price per Unit], SAMEPERIODLASTYEAR ( dim_date[Date] ) )
    MEASURE 'Key Measures'[Price YoY %] = DIVIDE ( [Avg Net Price per Unit] - [Avg Price PY], [Avg Price PY] )
    MEASURE 'Key Measures'[Title Revenue] = "Revenue " & FORMAT ( [Revenue], "$#,##0.0,,\M" ) & "  |  " & FORMAT ( [Revenue YoY %], "+0.0%;-0.0%" ) & " vs PY"
    MEASURE 'Key Measures'[Selected Region] = IF ( ISFILTERED ( dim_regions[region_name] ), SELECTEDVALUE ( dim_regions[region_name], "Multiple regions" ), "All regions" )

EVALUATE
    { [Revenue] }
```

Inside a `DEFINE` block, a measure can't start a new line with `VAR`, so `Top 10% Revenue Share` is written as a single expression there. The reference section below shows each measure on its own, formatted for reading.

---

## Date table

Create this in Modeling → New Table. Mark it as a date table (Table tools → Mark as date table → `Date`). The fiscal year starts October 1.

```dax
dim_date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2024, 10, 1 ), DATE ( 2026, 9, 30 ) ),
    "Year", YEAR ( [Date] ),
    "Month Num", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM" ),
    "Month Start", DATE ( YEAR ( [Date] ), MONTH ( [Date] ), 1 ),
    "Year-Month", FORMAT ( [Date], "YYYY-MM" ),
    "Fiscal Year", "FY" & FORMAT ( YEAR ( EDATE ( [Date], 3 ) ) - 2000, "00" ),
    "Fiscal Quarter", "FQ" & ROUNDUP ( MONTH ( EDATE ( [Date], 3 ) ) / 3, 0 ),
    "Fiscal Month Num", MONTH ( EDATE ( [Date], 3 ) ),
    "Weekday", FORMAT ( [Date], "ddd" ),
    "Weekday Num", WEEKDAY ( [Date], 2 )
)
```

Sort `Month` by `Fiscal Month Num` so October appears first.

---

## Calculated columns (on `fact_order_lines`)

```dax
Net Revenue = fact_order_lines[quantity] * fact_order_lines[unit_price] * ( 1 - fact_order_lines[discount_pct] )

COGS = fact_order_lines[quantity] * RELATED ( dim_products[unit_cost] )

Is Revenue Line = IF ( fact_order_lines[status] IN { "Delivered", "Shipped", "Pending" }, 1, 0 )
```

---

## Core KPIs  *(folder: 1 Core)*

```dax
Revenue =
CALCULATE ( SUM ( fact_order_lines[Net Revenue] ), fact_order_lines[Is Revenue Line] = 1 )

Gross Profit =
[Revenue] - CALCULATE ( SUM ( fact_order_lines[COGS] ), fact_order_lines[Is Revenue Line] = 1 )

Gross Margin % = DIVIDE ( [Gross Profit], [Revenue] )

Orders =
CALCULATE ( DISTINCTCOUNT ( fact_order_lines[order_id] ), fact_order_lines[Is Revenue Line] = 1 )

Avg Order Value = DIVIDE ( [Revenue], [Orders] )

Units Sold =
CALCULATE ( SUM ( fact_order_lines[quantity] ), fact_order_lines[Is Revenue Line] = 1 )

Active Customers =
CALCULATE ( DISTINCTCOUNT ( fact_order_lines[customer_id] ), fact_order_lines[Is Revenue Line] = 1 )

Avg Discount % =
AVERAGEX ( FILTER ( fact_order_lines, fact_order_lines[Is Revenue Line] = 1 ), fact_order_lines[discount_pct] )
```

## Time intelligence  *(folder: 2 Time)*

```dax
Revenue PY = CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( dim_date[Date] ) )

Revenue YoY % = DIVIDE ( [Revenue] - [Revenue PY], [Revenue PY] )

Revenue FYTD = TOTALYTD ( [Revenue], dim_date[Date], "9/30" )

Revenue PM = CALCULATE ( [Revenue], DATEADD ( dim_date[Date], -1, MONTH ) )

Revenue MoM % = DIVIDE ( [Revenue] - [Revenue PM], [Revenue PM] )

Revenue Rolling 3M =
CALCULATE ( [Revenue], DATESINPERIOD ( dim_date[Date], MAX ( dim_date[Date] ), -3, MONTH ) )

Revenue Running Total =
CALCULATE (
    [Revenue],
    FILTER ( ALLSELECTED ( dim_date[Date] ), dim_date[Date] <= MAX ( dim_date[Date] ) )
)
```

## Sales performance  *(folder: 3 Quota)*

`fact_sales_targets[month_start]` relates to `dim_date[Date]` (targets are stored on the 1st of each month).

```dax
Target = SUM ( fact_sales_targets[revenue_target] )

Quota Attainment % = DIVIDE ( [Revenue], [Target] )

Variance to Target = [Revenue] - [Target]

Attainment Color =
SWITCH ( TRUE (),
    [Quota Attainment %] >= 1,    "#2E7D32",
    [Quota Attainment %] >= 0.9,  "#F9A825",
    "#C62828"
)

Months Hit Target =
SUMX (
    VALUES ( dim_date[Month Start] ),
    IF ( [Revenue] >= [Target] && [Target] > 0, 1 )
)
```

Use `Attainment Color` in conditional formatting (Format → Data colors → fx → Field value).

## Returns & quality  *(folder: 4 Returns)*

```dax
Returned Lines = CALCULATE ( COUNTROWS ( fact_order_lines ), fact_order_lines[status] = "Returned" )

Return Rate % =
DIVIDE (
    [Returned Lines],
    CALCULATE ( COUNTROWS ( fact_order_lines ), fact_order_lines[status] <> "Cancelled" )
)

Revenue Lost to Returns =
CALCULATE ( SUM ( fact_order_lines[Net Revenue] ), fact_order_lines[status] = "Returned" )
```

## Customers  *(folder: 5 Customers)*

```dax
Last Order Date =
CALCULATE ( MAX ( fact_order_lines[order_date] ), fact_order_lines[Is Revenue Line] = 1 )

Days Since Last Order =
DATEDIFF ( [Last Order Date], DATE ( 2026, 9, 30 ), DAY )

At-Risk Customers =
COUNTROWS (
    FILTER (
        VALUES ( dim_customers[customer_id] ),
        [Days Since Last Order] > 90
            && CALCULATE ( [Revenue], dim_date[Fiscal Year] = "FY25" ) > 10000
    )
)

Customer Rank =
RANKX ( ALL ( dim_customers[customer_name] ), [Revenue], , DESC, DENSE )

Top 10% Revenue Share =
VAR TopCount = ROUNDUP ( COUNTROWS ( ALL ( dim_customers ) ) * 0.1, 0 )
VAR TopCust = TOPN ( TopCount, ALL ( dim_customers[customer_id] ), [Revenue], DESC )
RETURN DIVIDE ( CALCULATE ( [Revenue], TopCust ), CALCULATE ( [Revenue], ALL ( dim_customers ) ) )
```

## Pricing  *(folder: 6 Pricing)*

```dax
Avg Net Price per Unit = DIVIDE ( [Revenue], [Units Sold] )

Units PY = CALCULATE ( [Units Sold], SAMEPERIODLASTYEAR ( dim_date[Date] ) )

Units YoY % = DIVIDE ( [Units Sold] - [Units PY], [Units PY] )

Avg Price PY = CALCULATE ( [Avg Net Price per Unit], SAMEPERIODLASTYEAR ( dim_date[Date] ) )

Price YoY % = DIVIDE ( [Avg Net Price per Unit] - [Avg Price PY], [Avg Price PY] )
```

`Price YoY %` vs `Units YoY %` for the Dairy category is the evidence for the price-elasticity insight.

## Dynamic titles  *(folder: 7 Labels)*

```dax
Title Revenue =
"Revenue " & FORMAT ( [Revenue], "$#,##0.0,,\M" ) & "  |  " & FORMAT ( [Revenue YoY %], "+0.0%;-0.0%" ) & " vs PY"

Selected Region =
IF ( ISFILTERED ( dim_regions[region_name] ), SELECTEDVALUE ( dim_regions[region_name], "Multiple regions" ), "All regions" )
```
