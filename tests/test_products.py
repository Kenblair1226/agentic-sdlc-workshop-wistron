from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_products(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"][0]["name"] == "Zenbook 14 OLED"


def test_get_product(client: TestClient) -> None:
    response = client.get("/products/2")

    assert response.status_code == 200
    assert response.json()["name"] == "ROG Zephyrus G14"


def test_get_missing_product(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
