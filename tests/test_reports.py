"""Regression tests for the /reports/sales endpoint security fixes."""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Happy-path
# ---------------------------------------------------------------------------


def test_sales_report_returns_category_items_and_total(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop")

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Zenbook 14 OLED"
    assert body["total"] == 42900.0


def test_sales_report_formula_multiplier(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop&formula=total*1.1")

    assert response.status_code == 200
    assert abs(response.json()["total"] - 42900 * 1.1) < 0.01


def test_sales_report_formula_divisor(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop&formula=total/2")

    assert response.status_code == 200
    assert abs(response.json()["total"] - 42900 / 2) < 0.01


def test_sales_report_unknown_category_returns_empty(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Unknown")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0.0


# ---------------------------------------------------------------------------
# SQL injection
# ---------------------------------------------------------------------------


def test_sql_injection_in_category_is_neutralised(client: TestClient) -> None:
    """A SQL injection payload must not leak rows from other categories."""
    payload = "Laptop' OR '1'='1"
    response = client.get(f"/reports/sales?category={payload}")

    assert response.status_code == 200
    # Parameterised query treats the payload as a literal string, so no rows match.
    assert response.json()["items"] == []


def test_sql_injection_drop_table_is_neutralised(client: TestClient) -> None:
    payload = "Laptop'; DROP TABLE products;--"
    response = client.get(f"/reports/sales?category={payload}")

    assert response.status_code == 200
    assert response.json()["items"] == []


# ---------------------------------------------------------------------------
# Code / formula injection
# ---------------------------------------------------------------------------


def test_formula_eval_injection_is_rejected(client: TestClient) -> None:
    """Arbitrary Python expressions must not be executed."""
    response = client.get("/reports/sales?category=Laptop&formula=__import__('os').getpid()")

    assert response.status_code == 400
    # Must not expose a stack trace or exception details
    body = response.json()
    assert "traceback" not in str(body).lower()
    assert "import" not in str(body).lower()


def test_formula_arithmetic_expression_rejected(client: TestClient) -> None:
    """Only 'total', 'total*<n>', 'total/<n>' are valid – bare arithmetic is not."""
    response = client.get("/reports/sales?category=Laptop&formula=total+100")

    assert response.status_code == 400


def test_formula_division_by_zero_is_rejected(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop&formula=total/0")

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Error disclosure
# ---------------------------------------------------------------------------


def test_errors_do_not_expose_stack_traces(client: TestClient) -> None:
    """Internal errors must not leak tracebacks or implementation details."""
    # Use an overlong formula to trigger a validation error pathway.
    bad_formula = "x" * 200
    response = client.get(f"/reports/sales?category=Laptop&formula={bad_formula}")

    assert response.status_code in (400, 422, 500)
    text = response.text
    assert "traceback" not in text.lower()
    assert "sqlite" not in text.lower()
    assert "Traceback" not in text
