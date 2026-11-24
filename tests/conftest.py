import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    """Client de test avec une base SQLite temporaire."""
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db")})
    return app.test_client()


@pytest.fixture
def incident_data():
    return {"titre": "Projecteur HS", "description": "Ne s'allume plus", "lieu": "Salle B12", "priorite": "elevee"}
