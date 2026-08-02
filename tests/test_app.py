import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@mergington.edu for Chess Club"

    updated = client.get("/activities").json()
    assert "student@mergington.edu" in updated["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_from_activity(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert "Unregistered michael@mergington.edu from Chess Club" == response.json()["message"]

    activities_payload = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities_payload["Chess Club"]["participants"]
