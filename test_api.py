from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_expense():
    response = client.post("/expenses", json={
        "title": "Lunch",
        "amount": "150.00",
        "category": "Food",
        "expense_date": "2026-10-30",
        "description": "Lunch near office"
    })
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Lunch"
    assert created["amount"] == "150.00"

    fetched = client.get(f"/expenses/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]

def test_reject_non_positive_amount():
    response = client.post("/expenses", json={
        "title": "Invalid",
        "amount": "0",
        "category": "Other",
        "expense_date": "2026-10-30"
    })
    assert response.status_code == 422

def test_list_filter_and_summary():
    response = client.get("/expenses", params={"category": "Food"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    summary = client.get("/summary")
    assert summary.status_code == 200
    assert "total_amount" in summary.json()

def test_missing_expense_returns_404():
    response = client.get("/expenses/999999")
    assert response.status_code == 404
