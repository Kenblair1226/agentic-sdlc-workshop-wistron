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


ALLOWED_FORMULAS = {"total", "average", "count"}


def _apply_formula(formula: str, total: float, count: int) -> float:
    """Apply a safe, predefined formula to the sales data."""
    if formula == "total":
        return total
    if formula == "average":
        return total / count if count else 0.0
    if formula == "count":
        return float(count)
    raise ValueError(f"Unknown formula: {formula}")


@router.get("/sales", response_model=None)
def sales_report(
    category: str,
    formula: str = Query(default="total"),
) -> object:
    if formula not in ALLOWED_FORMULAS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid formula. Allowed: {', '.join(sorted(ALLOWED_FORMULAS))}"},
        )
    connection = create_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
        total = sum(row["price"] for row in rows)
        calculated_total = _apply_formula(formula, total, len(rows))
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
    finally:
        connection.close()
