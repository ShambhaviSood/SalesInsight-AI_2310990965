"""Backend test suite."""

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_upload_missing_file():
    response = client.post("/api/upload", data={"recipient_email": "test@example.com"})
    assert response.status_code == 422


def test_upload_invalid_email():
    csv_content = b"Product,Revenue\nWidget,1000"
    response = client.post(
        "/api/upload",
        data={"recipient_email": "not-an-email"},
        files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")},
    )
    assert response.status_code == 400


def test_upload_invalid_file_type():
    response = client.post(
        "/api/upload",
        data={"recipient_email": "test@example.com"},
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_empty_file():
    response = client.post(
        "/api/upload",
        data={"recipient_email": "test@example.com"},
        files={"file": ("test.csv", io.BytesIO(b""), "text/csv")},
    )
    assert response.status_code == 400


@patch("app.api.routes.send_summary_email", new_callable=AsyncMock)
@patch("app.api.routes.generate_summary", new_callable=AsyncMock)
def test_upload_success(mock_summary, mock_email):
    mock_summary.return_value = "## Executive Summary\nRevenue is great."
    mock_email.return_value = None

    csv_content = b"Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status\n2024-01-01,Electronics,North,100,50.0,5000.0,Completed"
    response = client.post(
        "/api/upload",
        data={"recipient_email": "test@example.com"},
        files={"file": ("sales.csv", io.BytesIO(csv_content), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data
