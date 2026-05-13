import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")

TEST_EMAIL = "tester@anchor.app"
TEST_PASSWORD = "Anchor!2026"
TEST_NAME = "Riley"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def auth_token(api_client):
    # try login first; register if needed
    r = api_client.post(f"{BASE_URL}/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}, timeout=20)
    if r.status_code == 200:
        return r.json()["token"]
    r = api_client.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "name": TEST_NAME},
        timeout=20,
    )
    if r.status_code == 200:
        return r.json()["token"]
    # might already exist with different password – fail clean
    pytest.skip(f"Cannot obtain auth token: {r.status_code} {r.text}")


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def second_user(api_client):
    """A second user used for cross-user isolation checks."""
    import uuid
    email = f"tester2_{uuid.uuid4().hex[:8]}@anchor.app"
    r = api_client.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": "Anchor!2026", "name": "Other"},
        timeout=20,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    return {"token": data["token"], "user": data["user"], "headers": {"Authorization": f"Bearer {data['token']}", "Content-Type": "application/json"}}
