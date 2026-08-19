import logging
import sqlite3

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)


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
            "WHERE category = ?"
        )
        rows = connection.execute(raw_query, (category,)).fetchall()
        total = sum(row["price"] for row in rows)

        if formula == "total":
            calculated_total = total
        elif formula == "double":
            calculated_total = total * 2
        elif formula == "with_tax":
            calculated_total = total * 1.07
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid formula"},
            )

        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except Exception:
        logger.exception("Failed to generate sales report")
        return JSONResponse(
            status_code=500,
            content={"error": "An internal error has occurred."},
        )
    finally:
        connection.close()
