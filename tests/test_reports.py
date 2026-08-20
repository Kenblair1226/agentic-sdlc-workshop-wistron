from fastapi.testclient import TestClient


def test_sales_report_returns_category_items_and_total(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop&formula=total")

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert body["items"] == [
        {
            "id": 1,
            "name": "Zenbook 14 OLED",
            "category": "Laptop",
            "price": 42900.0,
        }
    ]
    assert body["total"] == 42900.0


def test_sales_report_uses_parameterized_sql(client: TestClient) -> None:
    malicious_category = "Gaming Laptop' OR 1=1 --"
    response = client.get(
        "/reports/sales",
        params={"category": malicious_category, "formula": "total"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == malicious_category
    assert body["items"] == []
    assert body["total"] == 0.0


def test_sales_report_rejects_code_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('echo owned')"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body == {"detail": "Invalid formula"}
    assert "traceback" not in str(body).lower()


def test_sales_report_does_not_disclose_internal_errors(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total / 0"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body == {"detail": "Invalid formula"}
    assert "traceback" not in str(body).lower()
    assert "ZeroDivisionError" not in str(body)
