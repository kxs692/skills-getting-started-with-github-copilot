import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestBasicEndpoints:
    """Test basic API endpoints."""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client, reset_activities):
        """Test getting all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test activity signup functionality."""

    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity."""
        test_email = "test@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {test_email} for {activity_name}"
        
        # Verify the participant was added
        assert test_email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity."""
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signups are prevented."""
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"

    def test_signup_with_encoded_activity_name(self, client, reset_activities):
        """Test signup with URL-encoded activity name."""
        test_email = "test@mergington.edu"
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        # Verify the participant was added
        assert test_email in activities[activity_name]["participants"]

    def test_signup_with_encoded_email(self, client, reset_activities):
        """Test signup with URL-encoded email."""
        test_email = "test+special@mergington.edu"
        encoded_email = "test%2Bspecial%40mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify the participant was added
        assert test_email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test activity unregister functionality."""

    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity."""
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Verify participant is initially in the activity
        assert test_email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {test_email} from {activity_name}"
        
        # Verify the participant was removed
        assert test_email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity."""
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered_participant(self, client, reset_activities):
        """Test unregister participant who is not registered."""
        test_email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_unregister_with_encoded_parameters(self, client, reset_activities):
        """Test unregister with URL-encoded parameters."""
        test_email = "emma@mergington.edu"  # Already in Programming Class
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        encoded_email = "emma%40mergington.edu"
        
        # Verify participant is initially in the activity
        assert test_email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{encoded_name}/unregister?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify the participant was removed
        assert test_email not in activities[activity_name]["participants"]


class TestActivityCapacity:
    """Test activity capacity limits."""

    def test_activity_participant_count(self, client, reset_activities):
        """Test that participant counts are accurate."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert chess_club["max_participants"] == 12

    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow."""
        test_email = "workflow@mergington.edu"
        activity_name = "Science Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        new_count = len(response.json()[activity_name]["participants"])
        assert new_count == initial_count + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        final_count = len(response.json()[activity_name]["participants"])
        assert final_count == initial_count


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_missing_email_parameter(self, client, reset_activities):
        """Test signup without email parameter."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup")
        assert response.status_code == 422  # Validation error

    def test_empty_email_parameter(self, client, reset_activities):
        """Test signup with empty email parameter."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email=")
        assert response.status_code == 200  # FastAPI allows empty strings
        
        # Verify empty string was added (this might be considered a bug in real app)
        assert "" in activities[activity_name]["participants"]

    def test_special_characters_in_activity_name(self, client, reset_activities):
        """Test with special characters in activity name."""
        test_email = "test@mergington.edu"
        activity_name = "Activity & Special/Characters"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 404  # Activity doesn't exist