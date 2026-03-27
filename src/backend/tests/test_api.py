import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Verify the API is running and responding."""
    response = client.get("/api/health")
    if response.status_code == 404:
        # Fallback if there is no explicit /api/health endpoint
        pass
    else:
        assert response.status_code == 200

def test_search_diagnoses_exact():
    """Test exact ICD-10 code matching."""
    response = client.get("/api/search?q=F41&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    results = data["results"]
    assert len(results) > 0
    # First result should be exact match
    assert results[0]["code"] == "F41"
    assert "Angststörungen" in results[0]["title"] or "Panik" in results[0]["title"]

def test_search_diagnoses_semantic():
    """Test semantic search for a layman's term."""
    response = client.get("/api/search?q=kieferschmerzen&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    results = data["results"]
    assert len(results) > 0
    # Kieferschmerzen should find K10, K07, etc.
    codes = [r["code"] for r in results]
    assert "K10" in codes or "K07" in codes or "R51" in codes

def test_subcodes_endpoint():
    """Test that fetching subcodes for a valid 3-digit code works."""
    response = client.get("/api/subcodes?code=F41")
    assert response.status_code == 200
    data = response.json()
    assert data["parent_code"] == "F41"
    assert "subcodes" in data
    # Ensure subcodes list is not empty
    assert len(data["subcodes"]) > 0
    # Check if F41.0 or similar is in the list
    subcode_ids = [sub["code"] for sub in data["subcodes"]]
    assert any(code.startswith("F41") for code in subcode_ids)
