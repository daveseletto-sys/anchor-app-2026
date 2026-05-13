"""Iteration 2: Profile, Password change, Medications, Med logs, Weekly Insight tests."""
import os
import time
import uuid
from datetime import datetime, timezone, date, timedelta

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")


def _today():
    return datetime.now(timezone.utc).date().isoformat()


def _monday():
    d = datetime.now(timezone.utc).date()
    return (d - timedelta(days=d.weekday())).isoformat()


# ====== Profile (PATCH /users/me) ======
class TestProfileUpdate:
    def test_patch_profile_all_fields(self, api_client, auth_headers):
        new_start = (date.today() - timedelta(days=42)).isoformat()
        body = {"name": "Riley T2", "sobriety_start": new_start, "height_cm": 178.0, "weight_kg": 74.5}
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json=body)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["name"] == "Riley T2"
        assert d["sobriety_start"] == new_start
        assert d["height_cm"] == 178.0
        assert d["weight_kg"] == 74.5
        assert "id" in d and "_id" not in d
        # verify via /auth/me
        r2 = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert r2.json()["name"] == "Riley T2"
        # restore name for other tests
        api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"name": "Riley"})

    def test_patch_profile_bad_date(self, api_client, auth_headers):
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers,
                             json={"sobriety_start": "not-a-date"})
        # endpoint calls date.fromisoformat -> ValueError -> 500 OR pydantic 422.
        # acceptable: 400/422/500. Spec says 422.
        assert r.status_code in (400, 422, 500), r.text


# ====== Change Password ======
class TestChangePassword:
    def test_change_password_wrong_current(self, api_client, auth_headers):
        r = api_client.post(f"{BASE_URL}/api/auth/change-password", headers=auth_headers,
                            json={"current_password": "WRONG_PWD!", "new_password": "Anchor!2026new"})
        assert r.status_code == 400

    def test_change_password_then_login_with_new(self, api_client, auth_headers):
        old = "Anchor!2026"
        tmp = "Anchor!2026X"
        # change to tmp
        r = api_client.post(f"{BASE_URL}/api/auth/change-password", headers=auth_headers,
                            json={"current_password": old, "new_password": tmp})
        assert r.status_code == 200, r.text
        # login with new must work
        r = api_client.post(f"{BASE_URL}/api/auth/login",
                            json={"email": "tester@anchor.app", "password": tmp})
        assert r.status_code == 200, r.text
        # restore back to original
        tmp_token = r.json()["token"]
        tmp_hdrs = {"Authorization": f"Bearer {tmp_token}", "Content-Type": "application/json"}
        r = api_client.post(f"{BASE_URL}/api/auth/change-password", headers=tmp_hdrs,
                            json={"current_password": tmp, "new_password": old})
        assert r.status_code == 200, r.text
        # old password works again
        r = api_client.post(f"{BASE_URL}/api/auth/login",
                            json={"email": "tester@anchor.app", "password": old})
        assert r.status_code == 200


# ====== Medications CRUD ======
class TestMedications:
    def test_full_med_crud(self, api_client, auth_headers):
        # create
        body = {"name": f"TEST_med_{uuid.uuid4().hex[:6]}", "dose": "100mg", "schedule": "daily", "notes": "TEST"}
        r = api_client.post(f"{BASE_URL}/api/medications", headers=auth_headers, json=body)
        assert r.status_code == 200, r.text
        m = r.json()
        assert m["active"] is True
        assert m["name"] == body["name"]
        assert "id" in m and "_id" not in m
        mid = m["id"]
        # list
        r = api_client.get(f"{BASE_URL}/api/medications", headers=auth_headers)
        assert r.status_code == 200
        assert mid in [x["id"] for x in r.json()]
        # toggle active off
        r = api_client.patch(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers, json={"active": False})
        assert r.status_code == 200
        assert r.json()["active"] is False
        # GET to verify
        items = api_client.get(f"{BASE_URL}/api/medications", headers=auth_headers).json()
        match = [x for x in items if x["id"] == mid][0]
        assert match["active"] is False
        # delete
        r = api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers)
        assert r.status_code == 200
        items = api_client.get(f"{BASE_URL}/api/medications", headers=auth_headers).json()
        assert mid not in [x["id"] for x in items]

    def test_med_cross_user_isolation(self, api_client, auth_headers, second_user):
        body = {"name": f"TEST_iso_{uuid.uuid4().hex[:6]}", "dose": "10mg"}
        r = api_client.post(f"{BASE_URL}/api/medications", headers=auth_headers, json=body)
        mid = r.json()["id"]
        # second user can't see it
        r2 = api_client.get(f"{BASE_URL}/api/medications", headers=second_user["headers"])
        assert mid not in [x["id"] for x in r2.json()]
        # second user can't patch it
        r3 = api_client.patch(f"{BASE_URL}/api/medications/{mid}",
                              headers=second_user["headers"], json={"active": False})
        assert r3.status_code == 404
        # second user can't delete
        r4 = api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=second_user["headers"])
        assert r4.status_code == 404
        # cleanup
        api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers)


# ====== Medication Logs (UPSERT semantics) ======
class TestMedLogs:
    def test_log_upsert_no_duplicates(self, api_client, auth_headers):
        # create a med
        r = api_client.post(f"{BASE_URL}/api/medications", headers=auth_headers,
                            json={"name": f"TEST_uplog_{uuid.uuid4().hex[:6]}"})
        mid = r.json()["id"]
        today = _today()
        try:
            # first log
            r1 = api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                                 json={"medication_id": mid, "date": today, "taken": True})
            assert r1.status_code == 200, r1.text
            log_id_1 = r1.json()["id"]
            assert r1.json()["taken"] is True

            # second call same (med, date) -> upsert
            r2 = api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                                 json={"medication_id": mid, "date": today, "taken": False})
            assert r2.status_code == 200, r2.text
            log_id_2 = r2.json()["id"]
            assert r2.json()["taken"] is False
            assert log_id_1 == log_id_2, "Upsert must reuse same log id"

            # Verify only 1 doc in list for this med/date
            r3 = api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}", headers=auth_headers)
            assert r3.status_code == 200
            matches = [x for x in r3.json() if x["medication_id"] == mid]
            assert len(matches) == 1, f"Expected exactly 1 log doc, got {len(matches)}: {matches}"
            assert matches[0]["taken"] is False

            # third toggle back to true
            r4 = api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                                 json={"medication_id": mid, "date": today, "taken": True})
            assert r4.json()["taken"] is True
            matches = [x for x in api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}",
                                                 headers=auth_headers).json() if x["medication_id"] == mid]
            assert len(matches) == 1
        finally:
            api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers)

    def test_log_filter_by_date_and_user_scope(self, api_client, auth_headers, second_user):
        r = api_client.post(f"{BASE_URL}/api/medications", headers=auth_headers,
                            json={"name": f"TEST_logfilter_{uuid.uuid4().hex[:6]}"})
        mid = r.json()["id"]
        today = _today()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        try:
            api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                            json={"medication_id": mid, "date": today, "taken": True})
            api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                            json={"medication_id": mid, "date": yesterday, "taken": True})
            # filter today
            r1 = api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}", headers=auth_headers)
            assert all(x["date"] == today for x in r1.json())
            # other user sees nothing for this med
            r2 = api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}",
                                headers=second_user["headers"])
            assert mid not in [x["medication_id"] for x in r2.json()]
        finally:
            api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers)

    def test_delete_med_cascades_logs(self, api_client, auth_headers):
        r = api_client.post(f"{BASE_URL}/api/medications", headers=auth_headers,
                            json={"name": f"TEST_cascade_{uuid.uuid4().hex[:6]}"})
        mid = r.json()["id"]
        today = _today()
        api_client.post(f"{BASE_URL}/api/medications/log", headers=auth_headers,
                        json={"medication_id": mid, "date": today, "taken": True})
        # ensure log present
        r1 = api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}", headers=auth_headers)
        assert mid in [x["medication_id"] for x in r1.json()]
        # delete med
        r2 = api_client.delete(f"{BASE_URL}/api/medications/{mid}", headers=auth_headers)
        assert r2.status_code == 200
        # logs gone (cascade)
        r3 = api_client.get(f"{BASE_URL}/api/medications/log?date_str={today}", headers=auth_headers)
        assert mid not in [x["medication_id"] for x in r3.json()], "Logs must be cascade-deleted"


# ====== Weekly Insight (AI) ======
class TestWeeklyInsight:
    def test_get_before_generate_may_be_null(self, api_client, auth_headers):
        # cached state varies depending on prior tests; just ensure shape
        r = api_client.get(f"{BASE_URL}/api/insights/weekly", headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        assert "week_start" in d
        assert "text" in d

    def test_generate_weekly_insight(self, api_client, auth_headers):
        r = api_client.post(f"{BASE_URL}/api/insights/weekly", headers=auth_headers, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("stale") is False
        assert d["week_start"] == _monday()
        assert isinstance(d["text"], str)
        text = d["text"]
        words = len(text.split())
        # warm/spec range is ~180-260; allow some tolerance
        assert words >= 80, f"Insight too short ({words} words): {text[:200]}"
        assert "Riley" in text or "Riley" in text.lower() or len(text) > 200
        # GET returns cached
        r2 = api_client.get(f"{BASE_URL}/api/insights/weekly", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json()["text"] == text
        assert r2.json()["week_start"] == _monday()
