import sqlite3

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
        query = "SELECT id, name, category, price FROM products WHERE category = ?"
        rows = connection.execute(query, (category,)).fetchall()
        total = sum(row["price"] for row in rows)
        formula_map = {
            "total": total,
            "total_with_tax": total * 1.07,
            "total_with_discount": total * 0.90,
        }
        if formula not in formula_map:
            raise ValueError("Unsupported formula")
        calculated_total = formula_map[formula]
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "An internal error has occurred."},
        )
    finally:
        connection.close()
