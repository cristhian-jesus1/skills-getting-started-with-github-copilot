import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_participants = {
        activity_name: activity["participants"][:]
        for activity_name, activity in activities.items()
    }
    for activity in activities.values():
        activity["participants"].clear()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        for activity_name, participants in original_participants.items():
            activities[activity_name]["participants"][:] = participants


def test_get_activities_returns_activity_details_and_participants(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert response.json()[activity_name]["participants"] == []
    assert response.json()[activity_name]["max_participants"] == 12


def test_signup_adds_participant_to_activity(client):
    # Arrange
    activity_name = "Art Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    # Arrange
    activity_name = "Art Club"
    email = "student@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert activities[activity_name]["participants"] == [email]


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    activity_name = "Art Club"
    email = "student@mergington.edu"
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert client.get("/activities").json()[activity_name]["participants"] == []
