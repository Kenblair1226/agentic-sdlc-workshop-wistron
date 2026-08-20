import ast
import sqlite3
from typing import Any

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
            (4, "TUF Gaming A15", "Gaming Laptop", 38900),
            (5, "ROG Ally X", "Handheld", 26900),
            (6, "ProArt Display PA279CRV", "Monitor", 15900),
        ],
    )
    return connection


def evaluate_formula(formula: str, total: float) -> float:
    try:
        parsed = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid formula") from exc

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left**right
            raise ValueError("Invalid formula")
        if isinstance(node, ast.UnaryOp):
            operand = evaluate(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError("Invalid formula")
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError("Invalid formula")
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id == "total":
                return total
            raise ValueError("Invalid formula")
        raise ValueError("Invalid formula")

    return evaluate(parsed)


@router.get("/sales", response_model=None)
def sales_report(
    category: str,
    formula: str = Query(default="total", min_length=1, max_length=64),
) -> dict[str, Any]:
    connection = create_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
        total = sum(float(row["price"]) for row in rows)
        calculated_total = evaluate_formula(formula, total)
        return {
            "category": category,
            "items": [dict(row) for row in rows],
            "total": calculated_total,
        }
    except HTTPException:
        raise
    except (ArithmeticError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid formula",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sales report unavailable",
        ) from exc
    finally:
        connection.close()
