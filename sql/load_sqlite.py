"""Load the CSVs into a SQLite database (lakeshore.db) as raw_* tables,
then build the clean views from 01_build_and_clean.sql.

Usage (from the project folder):  python sql/load_sqlite.py
Then open lakeshore.db in DB Browser for SQLite or VS Code and run 02_business_questions.sql.
"""
import sqlite3, csv, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
db = sqlite3.connect(root / "lakeshore.db")
tables = {
    "raw_order_lines": "fact_order_lines.csv",
    "raw_targets": "fact_sales_targets.csv",
    "raw_customers": "dim_customers.csv",
    "raw_products": "dim_products.csv",
    "raw_sales_reps": "dim_sales_reps.csv",
    "raw_regions": "dim_regions.csv",
}
numeric = {"quantity", "unit_price", "discount_pct", "revenue_target", "list_price", "unit_cost", "line_number"}
for table, fname in tables.items():
    with open(root / "data" / fname, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    cols = ", ".join(f'"{h}" {"REAL" if h in numeric else "TEXT"}' for h in header)
    db.execute(f"DROP TABLE IF EXISTS {table}")
    db.execute(f"CREATE TABLE {table} ({cols})")
    data = [[None if v == "" else (float(v) if h in numeric else v) for h, v in zip(header, r)] for r in data]
    db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(header))})", data)
    print(f"{table}: {len(data):,} rows")

db.executescript((root / "sql" / "01_build_and_clean.sql").read_text())
db.commit()
print("Clean views built: customers, order_lines, sales")
