import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def setup_function():
    reset_activities()


def teardown_function():
    reset_activities()


def test_root_redirects_to_static_index():
    # Arrange
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "/static/index.html" in response.url.path


def test_get_activities_returns_available_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "description" in data[expected_activity]
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Art Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_registration_returns_400():
    # Arrange
    activity_name = "Art Club"
    duplicate_email = "duplicate_student@mergington.edu"

    # Act
    first_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )
    second_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already registered"


def test_signup_for_activity_returns_404_for_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Club"
    new_email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity_name = "Gym Class"
    remove_email = "john@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": remove_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {remove_email} from {activity_name}"}
    assert remove_email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_student():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "absent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
