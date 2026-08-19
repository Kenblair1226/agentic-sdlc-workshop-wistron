from fastapi.testclient import TestClient


def test_sales_report_normal(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop")
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Zenbook 14 OLED"
    assert body["total"] == 42900


def test_sales_report_no_match(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Nonexistent")
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Nonexistent"
    assert body["items"] == []
    assert body["total"] == 0


def test_sales_report_sql_injection(client: TestClient) -> None:
    response = client.get("/reports/sales?category=' OR '1'='1")
    assert response.status_code == 200
    # SQL injection must not return all rows; parameterized query treats it as literal
    body = response.json()
    assert body["items"] == []


def test_sales_report_code_injection_formula(client: TestClient) -> None:
    response = client.get(
        "/reports/sales?category=Laptop&formula=__import__('os').system('id')"
    )
    assert response.status_code == 400
    body = response.json()
    assert "detail" in body
    # Must not expose stack trace or Python internals
    assert "Traceback" not in body.get("detail", "")


def test_sales_report_invalid_formula(client: TestClient) -> None:
    response = client.get("/reports/sales?category=Laptop&formula=price*2")
    assert response.status_code == 400


def test_sales_report_empty_category(client: TestClient) -> None:
    response = client.get("/reports/sales?category=")
    assert response.status_code == 422


def test_sales_report_no_stack_trace_on_error(client: TestClient) -> None:
    # Even with weird input, responses must not expose stack traces
    response = client.get(
        "/reports/sales?category=Laptop&formula=__import__('os').getcwd()"
    )
    assert response.status_code == 400
    text = response.text
    assert "Traceback" not in text
    assert "File " not in text
