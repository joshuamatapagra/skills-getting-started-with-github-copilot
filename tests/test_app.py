from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def snapshot_activity(activity_name):
    return list(activities[activity_name]["participants"])


def restore_activity(activity_name, snapshot):
    activities[activity_name]["participants"] = list(snapshot)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic structure checks
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "test.user@example.com"
    original = snapshot_activity(activity)
    try:
        # ensure test email not present before starting
        if test_email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(test_email)

        # signup
        r = client.post(f"/activities/{activity}/signup", params={"email": test_email})
        assert r.status_code == 200
        assert test_email in activities[activity]["participants"]

        # duplicate signup should return 400
        r2 = client.post(f"/activities/{activity}/signup", params={"email": test_email})
        assert r2.status_code == 400

        # unregister
        r3 = client.delete(f"/activities/{activity}/signup", params={"email": test_email})
        assert r3.status_code == 200
        assert test_email not in activities[activity]["participants"]

    finally:
        # restore original participants to avoid side effects
        restore_activity(activity, original)
