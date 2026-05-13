"""Iteration 5 tests: /api/reports/email, /api/insights/email-digest, /api/milestones, /api/community/averages"""
import os
import uuid
import asyncio
import pytest
import requests
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")
VERIFIED_EMAIL = "daveseletto@gmail.com"  # Resend test-mode verified recipient


# -------- /api/reports/email --------

class TestReportsEmail:
    def test_email_report_unauth(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/reports/email",
            json={"recipient_email": VERIFIED_EMAIL, "period": "week", "scope": "clinical"},
            timeout=30,
        )
        assert r.status_code in (401, 403)

    def test_email_report_invalid_period(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/reports/email",
            headers=auth_headers,
            json={"recipient_email": VERIFIED_EMAIL, "period": "year", "scope": "clinical"},
            timeout=30,
        )
        assert r.status_code == 422, r.text

    def test_email_report_invalid_scope(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/reports/email",
            headers=auth_headers,
            json={"recipient_email": VERIFIED_EMAIL, "period": "week", "scope": "bogus"},
            timeout=30,
        )
        assert r.status_code == 422, r.text

    def test_email_report_test_mode_friendly_400(self, api_client, auth_headers):
        # Sending to an unverified recipient under Resend test mode -> 400 not 502
        r = api_client.post(
            f"{BASE_URL}/api/reports/email",
            headers=auth_headers,
            json={"recipient_email": "not-verified-user@example.com", "period": "week", "scope": "clinical"},
            timeout=60,
        )
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", "").lower()
        assert "test mode" in detail
        assert "verify a domain" in detail

    def test_email_report_happy_path(self, api_client, auth_headers):
        # Real send to Resend-verified address. May still fail in env without RESEND key configured.
        r = api_client.post(
            f"{BASE_URL}/api/reports/email",
            headers=auth_headers,
            json={"recipient_email": VERIFIED_EMAIL, "period": "week", "scope": "clinical", "note": "TEST_iter5 happy-path"},
            timeout=90,
        )
        if r.status_code == 503:
            pytest.skip("Email not configured in this env")
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        assert "email_id" in d


# -------- /api/insights/email-digest --------

class TestInsightDigestEmail:
    def test_digest_unauth(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/insights/email-digest", timeout=30)
        assert r.status_code in (401, 403)

    def test_digest_no_cached_insight(self, api_client, auth_headers, second_user):
        # second_user is fresh -> no weekly_insights row -> 400
        r = api_client.post(
            f"{BASE_URL}/api/insights/email-digest",
            headers=second_user["headers"],
            timeout=30,
        )
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", "")
        assert "No insight for this week yet" in detail

    def test_digest_with_cached_insight_test_mode_400(self, api_client, auth_headers):
        # Seed a cached insight directly via Mongo so we don't burn LLM calls
        from dotenv import load_dotenv
        load_dotenv("/app/backend/.env")
        mongo_url = os.environ["MONGO_URL"]
        db_name = os.environ["DB_NAME"]

        async def _seed():
            cli = AsyncIOMotorClient(mongo_url)
            try:
                # find user id by email
                u = await cli[db_name].users.find_one({"email": "tester@anchor.app"})
                today_dt = datetime.now(timezone.utc).date()
                monday = today_dt - timedelta(days=today_dt.weekday())
                await cli[db_name].weekly_insights.update_one(
                    {"user_id": u["id"], "week_start": monday.isoformat()},
                    {"$set": {
                        "user_id": u["id"],
                        "week_start": monday.isoformat(),
                        "text": "TEST insight body for iter5",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }},
                    upsert=True,
                )
            finally:
                cli.close()

        asyncio.run(_seed())
        # tester@anchor.app is NOT the Resend-verified email -> expect 400 test-mode message
        r = api_client.post(
            f"{BASE_URL}/api/insights/email-digest",
            headers=auth_headers,
            timeout=60,
        )
        if r.status_code == 503:
            pytest.skip("Email not configured")
        # acceptable: 400 test-mode OR 200 if user happens to be verified
        assert r.status_code in (200, 400), r.text
        if r.status_code == 400:
            detail = r.json().get("detail", "").lower()
            assert "test mode" in detail or "no insight for this week yet" in detail
        else:
            assert r.json().get("ok") is True


# -------- /api/milestones --------

class TestMilestones:
    REQUIRED_KEYS = {
        "current_streak_days", "best_protein_day", "best_protein_streak",
        "days_meeting_protein", "days_within_salt", "diet_days_logged",
        "diary_entries", "avg_rating_all_time", "best_rating_day",
        "best_7d_mood_avg", "best_7d_window_end", "med_adherence_30d_pct",
        "goals_completed",
    }

    def test_milestones_unauth(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/milestones", timeout=30)
        assert r.status_code in (401, 403)

    def test_milestones_shape(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/milestones", headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        missing = self.REQUIRED_KEYS - set(d.keys())
        assert not missing, f"missing keys: {missing}"
        assert isinstance(d["current_streak_days"], int)
        assert isinstance(d["diary_entries"], int)
        assert isinstance(d["goals_completed"], int)

    def test_milestones_cross_user_isolation(self, api_client, auth_headers, second_user):
        # second user: empty
        r2 = api_client.get(f"{BASE_URL}/api/milestones", headers=second_user["headers"], timeout=30)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["diary_entries"] == 0
        assert d2["diet_days_logged"] == 0
        assert d2["goals_completed"] == 0
        assert d2["best_protein_day"] in (None, {"date": None, "protein_g": 0})
        # primary user: add a meal + diary
        today = datetime.now(timezone.utc).date().isoformat()
        api_client.post(
            f"{BASE_URL}/api/meals",
            headers=auth_headers,
            json={"date": today, "name": "TEST_iter5_meal", "protein_g": 160, "salt_g": 1.5, "water_ml": 500, "calories": 600},
            timeout=20,
        )
        api_client.post(
            f"{BASE_URL}/api/diary",
            headers=auth_headers,
            json={"date": today, "rating": 9, "mood_tags": ["calm"], "notes": "TEST_iter5"},
            timeout=20,
        )
        # primary user milestones should reflect change
        r1 = api_client.get(f"{BASE_URL}/api/milestones", headers=auth_headers, timeout=30)
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["diary_entries"] >= 1
        assert d1["diet_days_logged"] >= 1
        assert d1["days_meeting_protein"] >= 1
        # second user must still be empty
        r2b = api_client.get(f"{BASE_URL}/api/milestones", headers=second_user["headers"], timeout=30)
        d2b = r2b.json()
        assert d2b["diary_entries"] == 0
        assert d2b["diet_days_logged"] == 0


# -------- /api/community/averages --------

class TestCommunityAverages:
    def test_community_unauth(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/community/averages", timeout=30)
        assert r.status_code in (401, 403)

    def test_community_shape_and_privacy(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/community/averages", headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        # mandatory keys
        for k in ("users_count", "user_days", "avg_protein_g", "avg_salt_g", "avg_water_ml",
                  "avg_mood", "targets", "min_users_threshold"):
            assert k in d, f"missing {k}"
        assert d["min_users_threshold"] == 5
        # if fewer than threshold, averages must be null
        if d["users_count"] < 5:
            assert d["avg_protein_g"] is None
            assert d["avg_salt_g"] is None
            assert d["avg_water_ml"] is None
            assert d["avg_mood"] is None
        else:
            # else they may be numeric or null only if no meals at all
            for k in ("avg_protein_g", "avg_salt_g", "avg_water_ml"):
                assert d[k] is None or isinstance(d[k], (int, float))
