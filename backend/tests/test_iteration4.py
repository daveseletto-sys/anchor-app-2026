"""Iteration 4 tests: /api/correlations + /api/share-links + /api/shared/{token}"""
import os
import uuid
import pytest
import requests
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")


# -------- /api/correlations --------

class TestCorrelations:
    def test_correlations_default_30(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/correlations?days=30", headers=auth_headers, timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["days"] == 30
        assert isinstance(d["series"], list)
        assert len(d["series"]) == 30
        s0 = d["series"][0]
        for k in ("date", "rating", "protein_g", "salt_g", "water_ml"):
            assert k in s0
        # correlations object
        c = d["correlations"]
        assert set(c.keys()) >= {"protein", "salt", "water", "n"}
        assert isinstance(c["n"], int)

    def test_correlations_custom_days(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/correlations?days=7", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert len(r.json()["series"]) == 7

    def test_correlations_out_of_range_high(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/correlations?days=400", headers=auth_headers, timeout=20)
        assert r.status_code == 422

    def test_correlations_out_of_range_low(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/correlations?days=0", headers=auth_headers, timeout=20)
        assert r.status_code == 422

    def test_correlations_unauth(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/correlations?days=30", timeout=20)
        assert r.status_code in (401, 403)

    def test_correlations_n_lt_3_returns_null(self, api_client, auth_headers):
        # When there are fewer than 3 paired (rating + diet) days, correlations should be null
        r = api_client.get(f"{BASE_URL}/api/correlations?days=1", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        c = r.json()["correlations"]
        if c["n"] < 3:
            assert c["protein"] is None
            assert c["salt"] is None
            assert c["water"] is None


# -------- /api/share-links --------

class TestShareLinksCRUD:
    created_ids = []

    def test_create_summary_link(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "summary"},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        for k in ("id", "token", "scope", "expires_at", "revoked", "created_at"):
            assert k in d
        assert d["scope"] == "summary"
        assert d["revoked"] is False
        # url-safe token ~32 chars
        assert 30 <= len(d["token"]) <= 64
        # never expose user_id / _id
        assert "user_id" not in d
        assert "_id" not in d
        TestShareLinksCRUD.created_ids.append(d["id"])

    def test_create_full_scope(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 14, "scope": "full"},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        assert r.json()["scope"] == "full"
        TestShareLinksCRUD.created_ids.append(r.json()["id"])

    def test_create_invalid_scope(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "bogus"},
            timeout=20,
        )
        assert r.status_code == 422

    def test_create_expires_zero(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 0, "scope": "summary"},
            timeout=20,
        )
        assert r.status_code == 422

    def test_create_expires_91(self, api_client, auth_headers):
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 91, "scope": "summary"},
            timeout=20,
        )
        assert r.status_code == 422

    def test_list_share_links(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/share-links", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 2
        # never includes user_id / _id
        for it in items:
            assert "user_id" not in it
            assert "_id" not in it
        # sorted by created_at desc
        ts = [it["created_at"] for it in items]
        assert ts == sorted(ts, reverse=True)

    def test_list_isolated_to_user(self, api_client, auth_headers, second_user):
        r = api_client.get(f"{BASE_URL}/api/share-links", headers=second_user["headers"], timeout=20)
        assert r.status_code == 200
        assert r.json() == []  # second user has no links

    def test_delete_revoke(self, api_client, auth_headers):
        # create a fresh one to revoke
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "summary"},
            timeout=20,
        )
        link_id = r.json()["id"]
        rd = api_client.delete(f"{BASE_URL}/api/share-links/{link_id}", headers=auth_headers, timeout=20)
        assert rd.status_code == 200
        # verify revoked=true
        lst = api_client.get(f"{BASE_URL}/api/share-links", headers=auth_headers, timeout=20).json()
        match = [x for x in lst if x["id"] == link_id]
        assert match and match[0]["revoked"] is True

    def test_delete_other_user_link_404(self, api_client, auth_headers, second_user):
        # Make link as primary, try to revoke as second user
        r = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "summary"},
            timeout=20,
        )
        link_id = r.json()["id"]
        rd = api_client.delete(f"{BASE_URL}/api/share-links/{link_id}", headers=second_user["headers"], timeout=20)
        assert rd.status_code == 404


# -------- /api/shared/{token} (PUBLIC) --------

class TestSharedView:
    def test_shared_404(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/shared/nonexistent-token-12345", timeout=20)
        assert r.status_code == 404

    def test_shared_public_summary(self, api_client, auth_headers):
        # create a summary link
        cr = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "summary"},
            timeout=20,
        )
        token = cr.json()["token"]
        # Hit without auth
        r = requests.get(f"{BASE_URL}/api/shared/{token}", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        for k in ("owner_name", "expires_at", "scope", "sobriety", "diet_summary", "diary_avg_rating", "goals", "diary_entries"):
            assert k in d
        assert d["scope"] == "summary"
        assert d["diary_entries"] == []  # empty for summary
        assert "days_sober" in d["sobriety"]
        assert "sobriety_start" in d["sobriety"]

    def test_shared_full_scope_returns_diary(self, api_client, auth_headers):
        # ensure at least one diary entry exists for today
        today = datetime.now(timezone.utc).date().isoformat()
        api_client.post(
            f"{BASE_URL}/api/diary",
            headers=auth_headers,
            json={"date": today, "rating": 7, "mood_tags": ["calm"], "notes": "shared-test"},
            timeout=20,
        )
        cr = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "full"},
            timeout=20,
        )
        token = cr.json()["token"]
        r = requests.get(f"{BASE_URL}/api/shared/{token}", timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert d["scope"] == "full"
        # diary_entries must have shape {date, rating, mood_tags}
        if d["diary_entries"]:
            e = d["diary_entries"][0]
            assert "date" in e and "rating" in e and "mood_tags" in e

    def test_shared_revoked_returns_410(self, api_client, auth_headers):
        cr = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 7, "scope": "summary"},
            timeout=20,
        )
        link_id = cr.json()["id"]
        token = cr.json()["token"]
        api_client.delete(f"{BASE_URL}/api/share-links/{link_id}", headers=auth_headers, timeout=20)
        r = requests.get(f"{BASE_URL}/api/shared/{token}", timeout=20)
        assert r.status_code == 410

    def test_shared_expired_returns_410(self, api_client, auth_headers):
        cr = api_client.post(
            f"{BASE_URL}/api/share-links",
            headers=auth_headers,
            json={"expires_in_days": 1, "scope": "summary"},
            timeout=20,
        )
        link_id = cr.json()["id"]
        token = cr.json()["token"]

        # Backdate expires_at via direct Mongo update
        mongo_url = os.environ["MONGO_URL"]
        db_name = os.environ["DB_NAME"]

        async def _backdate():
            cli = AsyncIOMotorClient(mongo_url)
            try:
                past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
                await cli[db_name].share_links.update_one({"id": link_id}, {"$set": {"expires_at": past}})
            finally:
                cli.close()

        asyncio.get_event_loop().run_until_complete(_backdate()) if False else asyncio.run(_backdate())
        r = requests.get(f"{BASE_URL}/api/shared/{token}", timeout=20)
        assert r.status_code == 410
