from fastapi.testclient import TestClient


def test_sales_report_normal(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Zenbook 14 OLED"
    assert body["total"] == 42900


def test_sales_report_no_match(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Nonexistent"})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_sales_report_sql_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "' OR '1'='1"},
    )

    assert response.status_code == 200
    body = response.json()
    # Parameterized query should treat the whole string as a literal category
    assert body["items"] == []


def test_sales_report_code_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('echo pwned')"},
    )

    assert response.status_code == 400
    assert "Invalid formula" in response.json()["error"]


def test_sales_report_error_no_stack_trace(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "bad_formula"},
    )

    assert response.status_code == 400
    body = response.json()
    assert "Traceback" not in body.get("error", "")
    assert "File" not in body.get("error", "")
