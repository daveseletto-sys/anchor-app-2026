"""Iteration 3: Crisis hotlines + Clinician PDF export tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")


# ---- Crisis hotlines ----
class TestCrisis:
    def test_reset_region_to_both(self, api_client, auth_headers):
        # Clear region first
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"region": ""})
        # empty string is treated as None by helper; should be 200
        assert r.status_code == 200, r.text
        # /auth/me should show region=null
        me = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers).json()
        assert me.get("region") in (None, ""), me

    def test_crisis_no_region(self, api_client, auth_headers):
        # ensure cleared
        api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"region": ""})
        r = api_client.get(f"{BASE_URL}/api/crisis", headers=auth_headers)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["region"] is None
        assert sorted(d["regions"]) == ["UK", "US"]
        assert isinstance(d["hotlines"], dict)
        assert "US" in d["hotlines"] and "UK" in d["hotlines"]
        assert len(d["hotlines"]["US"]) == 5
        assert len(d["hotlines"]["UK"]) == 6
        for h in d["hotlines"]["US"] + d["hotlines"]["UK"]:
            assert "name" in h and "url" in h and "description" in h

    def test_patch_region_us(self, api_client, auth_headers):
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"region": "US"})
        assert r.status_code == 200, r.text
        assert r.json()["region"] == "US"
        me = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers).json()
        assert me["region"] == "US"
        # crisis
        c = api_client.get(f"{BASE_URL}/api/crisis", headers=auth_headers).json()
        assert c["region"] == "US"
        assert c["regions"] == ["US"]
        assert isinstance(c["hotlines"], list)
        assert len(c["hotlines"]) == 5

    def test_patch_region_uk(self, api_client, auth_headers):
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"region": "UK"})
        assert r.status_code == 200, r.text
        assert r.json()["region"] == "UK"
        c = api_client.get(f"{BASE_URL}/api/crisis", headers=auth_headers).json()
        assert c["region"] == "UK"
        assert c["regions"] == ["UK"]
        assert isinstance(c["hotlines"], list)
        assert len(c["hotlines"]) == 6

    def test_patch_region_invalid(self, api_client, auth_headers):
        r = api_client.patch(f"{BASE_URL}/api/users/me", headers=auth_headers, json={"region": "INVALID"})
        assert r.status_code == 422, r.text

    def test_crisis_requires_auth(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/crisis")
        assert r.status_code in (401, 403)


# ---- PDF Reports ----
class TestReportsPDF:
    def _assert_pdf(self, r, min_size=1000):
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd.lower()
        assert "filename" in cd.lower()
        body = r.content
        assert body[:4] == b"%PDF", f"Not a PDF, starts with {body[:8]}"
        assert len(body) > min_size, f"PDF too small: {len(body)} bytes"
        return body

    def test_pdf_week_clinical(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=week&scope=clinical", headers=auth_headers)
        self._assert_pdf(r)

    def test_pdf_month_full(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=month&scope=full", headers=auth_headers)
        body = self._assert_pdf(r)
        # heuristically full PDF often >= clinical week, but not guaranteed if no diary; just check ok
        assert len(body) >= 1500

    def test_pdf_week_personal(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=week&scope=personal", headers=auth_headers)
        self._assert_pdf(r)

    def test_pdf_invalid_period(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=invalid&scope=clinical", headers=auth_headers)
        assert r.status_code == 422, r.text

    def test_pdf_invalid_scope(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=week&scope=invalid", headers=auth_headers)
        assert r.status_code == 422, r.text

    def test_pdf_no_auth(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=week&scope=clinical")
        assert r.status_code in (401, 403)

    def test_pdf_filename_contains_period_scope(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/reports/pdf?period=week&scope=clinical", headers=auth_headers)
        cd = r.headers.get("content-disposition", "")
        assert "week" in cd and "clinical" in cd

    def teardown_class(cls):
        # restore region to "both" for downstream tests/users
        try:
            r = requests.post(f"{BASE_URL}/api/auth/login",
                              json={"email": "tester@anchor.app", "password": "Anchor!2026"}, timeout=10)
            if r.status_code == 200:
                tok = r.json()["token"]
                requests.patch(f"{BASE_URL}/api/users/me",
                               headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                               json={"region": ""}, timeout=10)
        except Exception:
            pass
