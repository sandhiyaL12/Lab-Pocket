import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


@pytest.fixture
def client(tmp_path):
    app.dependency_overrides[get_settings] = lambda: Settings(
        app_name="Lab-Pocket",
        environment="test",
        cost_log_path=str(tmp_path / "cost-log.jsonl"),
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
