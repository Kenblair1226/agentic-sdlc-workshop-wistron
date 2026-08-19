import sqlite3
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

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


def _apply_formula(formula: str, total: float) -> float:
    """Apply a simple multiplicative formula to the total.

    Only ``total``, ``total*<number>``, and ``total/<number>`` are accepted.
    This avoids any use of ``eval`` while still supporting common adjustments
    like applying a tax rate or discount.
    """
    formula = formula.strip()
    if formula == "total":
        return total
    for op in ("*", "/"):
        if formula.startswith(f"total{op}"):
            factor_str = formula[len(f"total{op}"):].strip()
            try:
                factor = float(factor_str)
            except ValueError:
                break
            if op == "*":
                return total * factor
            if factor == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Division by zero in formula.",
                )
            return total / factor
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid formula. Allowed forms: 'total', 'total*<number>', 'total/<number>'.",
    )


@router.get("/sales", response_model=None)
def sales_report(
    category: Annotated[str, Query(max_length=100)],
    formula: Annotated[str, Query(max_length=50)] = "total",
) -> object:
    connection = create_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
        total = sum(row["price"] for row in rows)
        calculated_total = _apply_formula(formula, total)
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        ) from exc
    finally:
        connection.close()
