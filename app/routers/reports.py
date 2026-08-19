import sqlite3
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/reports", tags=["reports"])

_ALLOWED_FORMULAS: dict[str, str] = {
    "total": "total",
}


def _create_database() -> sqlite3.Connection:
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
    category: Annotated[str, Query(min_length=1, max_length=100)],
    formula: str = Query(default="total"),
) -> object:
    if formula not in _ALLOWED_FORMULAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid formula. Allowed values: total",
        )

    connection = _create_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
        total = sum(row["price"] for row in rows)
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": total,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        ) from exc
    finally:
        connection.close()
