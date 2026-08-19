from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "app" / "main.py"
REPORTS_PATH = ROOT / "app" / "routers" / "reports.py"

IMPORT_LINE = "from app.routers import products, reports"
ORIGINAL_IMPORT_LINE = "from app.routers import products"
INCLUDE_LINE = "app.include_router(reports.router)"

INSECURE_REPORTS = '''\
import sqlite3
import traceback

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/reports", tags=["reports"])


def create_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL)"
    )
    connection.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [
            (1, "Zenbook 14 OLED", "Laptop", 42900),
            (2, "ROG Zephyrus G14", "Gaming Laptop", 62900),
            (3, "ProArt P16", "Creator Laptop", 79900),
        ],
    )
    return connection


@router.get("/sales", response_model=None)
def sales_report(
    category: str,
    formula: str = Query(default="total"),
) -> object:
    connection = create_database()
    try:
        raw_query = (
            "SELECT id, name, category, price FROM products "
            f"WHERE category = '{category}'"
        )
        rows = connection.execute(raw_query).fetchall()
        total = sum(row["price"] for row in rows)
        calculated_total = eval(formula, {"__builtins__": {}}, {"total": total})
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": traceback.format_exc()},
        )
    finally:
        connection.close()
'''


def prepare() -> None:
    main_content = MAIN_PATH.read_text(encoding="utf-8")
    if REPORTS_PATH.exists() or IMPORT_LINE in main_content or INCLUDE_LINE in main_content:
        raise SystemExit(
            "Lab 2 files already appear to be prepared. "
            "Run `python scripts/prepare_lab2.py --reset` before preparing it again."
        )

    if ORIGINAL_IMPORT_LINE not in main_content:
        raise SystemExit("Could not find the expected products router import in app/main.py.")

    REPORTS_PATH.write_text(INSECURE_REPORTS, encoding="utf-8")
    main_content = main_content.replace(ORIGINAL_IMPORT_LINE, IMPORT_LINE, 1)
    main_content = main_content.replace(
        "app.include_router(products.router)",
        f"app.include_router(products.router)\n{INCLUDE_LINE}",
        1,
    )
    MAIN_PATH.write_text(main_content, encoding="utf-8")
    print("Lab 2 insecure endpoint prepared.")
    print("Review the diff, then commit it on a dedicated lab2-insecure-report branch.")


def reset() -> None:
    main_content = MAIN_PATH.read_text(encoding="utf-8")
    main_content = main_content.replace(IMPORT_LINE, ORIGINAL_IMPORT_LINE, 1)
    main_content = main_content.replace(f"\n{INCLUDE_LINE}", "", 1)
    MAIN_PATH.write_text(main_content, encoding="utf-8")
    REPORTS_PATH.unlink(missing_ok=True)
    print("Lab 2 generated files and router registration removed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare or reset the Lab 2 insecure change.")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    reset() if args.reset else prepare()


if __name__ == "__main__":
    main()
