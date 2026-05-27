import copy
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activity_dictionary():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "testuser@example.com"
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Drama Club"
    email = "missing@example.com"
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
