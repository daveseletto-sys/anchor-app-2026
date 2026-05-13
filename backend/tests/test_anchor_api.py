"""Backend API regression tests for Anchor Recovery app."""
import os
import base64
import io
import uuid
from datetime import datetime, timezone, date, timedelta

import pytest
import requests
from PIL import Image, ImageDraw, ImageFont

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://progress-hub-256.preview.emergentagent.com").rstrip("/")


# -------- helpers --------

def _today():
    return datetime.now(timezone.utc).date().isoformat()


def _monday():
    d = datetime.now(timezone.utc).date()
    return (d - timedelta(days=d.weekday())).isoformat()


def _make_label_image_b64() -> str:
    """Create a realistic-looking nutrition label image with text/edges/shadows."""
    img = Image.new("RGB", (520, 720), (252, 248, 240))
    d = ImageDraw.Draw(img)
    # bold border
    d.rectangle([6, 6, 514, 714], outline=(20, 20, 20), width=4)
    # title
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font_big = font_med = font_sm = ImageFont.load_default()
    d.text((24, 18), "Nutrition Facts", fill=(0, 0, 0), font=font_big)
    d.line([(24, 72), (496, 72)], fill=(0, 0, 0), width=6)
    d.text((24, 86), "Serving size 100 g", fill=(0, 0, 0), font=font_sm)
    d.line([(24, 120), (496, 120)], fill=(0, 0, 0), width=2)
    lines = [
        ("Calories", "180"),
        ("Total Fat", "5 g"),
        ("Sodium", "400 mg"),
        ("Total Carbs", "20 g"),
        ("Sugars", "3 g"),
        ("Protein", "25 g"),
        ("Salt", "1.0 g"),
    ]
    y = 138
    for k, v in lines:
        d.text((28, y), k, fill=(0, 0, 0), font=font_med)
        d.text((380, y), v, fill=(0, 0, 0), font=font_med)
        d.line([(24, y + 34), (496, y + 34)], fill=(80, 80, 80), width=1)
        y += 50
    # subtle shadow rectangle for texture
    d.rectangle([300, 600, 480, 680], outline=(120, 120, 120), width=2)
    d.text((312, 622), "Brand: Acme", fill=(60, 60, 60), font=font_sm)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _make_blood_report_b64() -> str:
    """Create a synthetic blood test report image."""
    img = Image.new("RGB", (640, 760), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, 636, 756], outline=(0, 0, 0), width=3)
    try:
        font_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font_t = font_h = font_b = ImageFont.load_default()
    d.text((20, 16), "Acme Diagnostics Lab", fill=(0, 0, 0), font=font_t)
    d.text((20, 60), "Patient: Test Patient    Date: 2026-01-10", fill=(40, 40, 40), font=font_b)
    d.line([(20, 96), (620, 96)], fill=(0, 0, 0), width=2)
    headers = ["Marker", "Value", "Unit", "Reference"]
    xs = [24, 240, 360, 460]
    for x, h in zip(xs, headers):
        d.text((x, 104), h, fill=(0, 0, 0), font=font_h)
    d.line([(20, 138), (620, 138)], fill=(0, 0, 0), width=1)
    rows = [
        ("ALT (SGPT)", "42", "U/L", "7-56"),
        ("AST (SGOT)", "38", "U/L", "10-40"),
        ("GGT", "55", "U/L", "9-48"),
        ("ALP", "98", "U/L", "44-147"),
        ("Bilirubin Total", "0.9", "mg/dL", "0.1-1.2"),
        ("Albumin", "4.2", "g/dL", "3.5-5.0"),
        ("MCV", "92", "fL", "80-100"),
    ]
    y = 148
    for r in rows:
        for x, val in zip(xs, r):
            d.text((x, y), val, fill=(0, 0, 0), font=font_b)
        d.line([(20, y + 32), (620, y + 32)], fill=(180, 180, 180), width=1)
        y += 44
    # shadows for texture
    d.rectangle([400, 540, 600, 600], outline=(150, 150, 150), width=2)
    d.text((412, 558), "Signed: Dr. A", fill=(80, 80, 80), font=font_b)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# =========================================================================
# AUTH
# =========================================================================
class TestAuth:
    def test_root(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        assert r.json().get("ok") is True

    def test_login_or_register(self, auth_token):
        assert isinstance(auth_token, str) and len(auth_token) > 20

    def test_login_invalid(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/auth/login", json={"email": "no-such@x.com", "password": "wrong"})
        assert r.status_code == 401

    def test_register_duplicate(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/auth/register", json={"email": "tester@anchor.app", "password": "Anchor!2026", "name": "Riley"})
        assert r.status_code == 400

    def test_me_with_token(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "tester@anchor.app"
        assert "id" in data and "_id" not in data

    def test_me_without_token(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401


# =========================================================================
# SOBRIETY
# =========================================================================
class TestSobriety:
    def test_get_sobriety(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/sobriety", headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        assert "days_sober" in d and "sobriety_start" in d
        assert isinstance(d["days_sober"], int)
        assert d["days_sober"] >= 0

    def test_patch_sobriety(self, api_client, auth_headers):
        new_start = (date.today() - timedelta(days=10)).isoformat()
        r = api_client.patch(f"{BASE_URL}/api/sobriety", headers=auth_headers, json={"sobriety_start": new_start})
        assert r.status_code == 200
        d = r.json()
        assert d["sobriety_start"] == new_start
        assert d["days_sober"] == 10
        # verify via GET
        r2 = api_client.get(f"{BASE_URL}/api/sobriety", headers=auth_headers)
        assert r2.json()["sobriety_start"] == new_start


# =========================================================================
# DIARY
# =========================================================================
class TestDiary:
    def test_create_list_delete_diary(self, api_client, auth_headers):
        # create
        payload = {"date": _today(), "rating": 7, "mood_tags": ["calm", "hopeful"], "notes": "TEST_diary"}
        r = api_client.post(f"{BASE_URL}/api/diary", headers=auth_headers, json=payload)
        assert r.status_code == 200, r.text
        e = r.json()
        assert e["rating"] == 7
        assert e["mood_tags"] == ["calm", "hopeful"]
        assert "id" in e and "_id" not in e
        eid = e["id"]
        # list
        r = api_client.get(f"{BASE_URL}/api/diary", headers=auth_headers)
        assert r.status_code == 200
        ids = [x["id"] for x in r.json()]
        assert eid in ids
        # delete
        r = api_client.delete(f"{BASE_URL}/api/diary/{eid}", headers=auth_headers)
        assert r.status_code == 200
        # verify gone
        r = api_client.get(f"{BASE_URL}/api/diary", headers=auth_headers)
        assert eid not in [x["id"] for x in r.json()]

    def test_diary_cross_user_isolation(self, api_client, auth_headers, second_user):
        payload = {"date": _today(), "rating": 5, "mood_tags": [], "notes": "TEST_iso"}
        r = api_client.post(f"{BASE_URL}/api/diary", headers=auth_headers, json=payload)
        eid = r.json()["id"]
        # other user cannot delete
        r2 = api_client.delete(f"{BASE_URL}/api/diary/{eid}", headers=second_user["headers"])
        assert r2.status_code == 404
        # cleanup
        api_client.delete(f"{BASE_URL}/api/diary/{eid}", headers=auth_headers)

    def test_diary_rating_validation(self, api_client, auth_headers):
        r = api_client.post(f"{BASE_URL}/api/diary", headers=auth_headers, json={"date": _today(), "rating": 11, "mood_tags": [], "notes": ""})
        assert r.status_code == 422


# =========================================================================
# MEALS / WATER
# =========================================================================
class TestMeals:
    def test_meal_crud_and_totals(self, api_client, auth_headers):
        today = _today()
        # baseline totals
        r = api_client.get(f"{BASE_URL}/api/meals/totals?date_str={today}", headers=auth_headers)
        assert r.status_code == 200
        base = r.json()["totals"]
        # add meal
        meal = {"date": today, "name": "TEST_meal", "protein_g": 30, "salt_g": 0.5, "water_ml": 250, "calories": 400}
        r = api_client.post(f"{BASE_URL}/api/meals", headers=auth_headers, json=meal)
        assert r.status_code == 200
        mid = r.json()["id"]
        # filter list by date
        r = api_client.get(f"{BASE_URL}/api/meals?date_str={today}", headers=auth_headers)
        assert r.status_code == 200
        assert mid in [m["id"] for m in r.json()]
        # totals reflect addition
        r = api_client.get(f"{BASE_URL}/api/meals/totals?date_str={today}", headers=auth_headers)
        nt = r.json()["totals"]
        assert abs(nt["protein_g"] - (base["protein_g"] + 30)) < 0.01
        assert abs(nt["calories"] - (base["calories"] + 400)) < 0.01
        # delete
        r = api_client.delete(f"{BASE_URL}/api/meals/{mid}", headers=auth_headers)
        assert r.status_code == 200

    def test_quick_water(self, api_client, auth_headers):
        today = _today()
        r = api_client.get(f"{BASE_URL}/api/meals/totals?date_str={today}", headers=auth_headers)
        base_water = r.json()["totals"]["water_ml"]
        r = api_client.post(f"{BASE_URL}/api/water", headers=auth_headers, json={"date": today, "amount_ml": 300})
        assert r.status_code == 200
        mid = r.json()["id"]
        assert r.json()["water_ml"] == 300
        r = api_client.get(f"{BASE_URL}/api/meals/totals?date_str={today}", headers=auth_headers)
        assert abs(r.json()["totals"]["water_ml"] - (base_water + 300)) < 0.01
        api_client.delete(f"{BASE_URL}/api/meals/{mid}", headers=auth_headers)


# =========================================================================
# BLOOD TESTS
# =========================================================================
class TestBloodTests:
    def test_blood_crud(self, api_client, auth_headers):
        payload = {
            "date": _today(),
            "lab": "TEST_lab",
            "markers": [{"name": "ALT", "value": 42, "unit": "U/L", "reference_range": "7-56"}],
            "notes": "TEST_bt",
        }
        r = api_client.post(f"{BASE_URL}/api/blood-tests", headers=auth_headers, json=payload)
        assert r.status_code == 200, r.text
        bid = r.json()["id"]
        assert r.json()["markers"][0]["name"] == "ALT"
        # list
        r = api_client.get(f"{BASE_URL}/api/blood-tests", headers=auth_headers)
        assert bid in [b["id"] for b in r.json()]
        # delete
        r = api_client.delete(f"{BASE_URL}/api/blood-tests/{bid}", headers=auth_headers)
        assert r.status_code == 200

    def test_blood_extract_from_image(self, api_client, auth_headers):
        b64 = _make_blood_report_b64()
        r = api_client.post(
            f"{BASE_URL}/api/blood-tests/extract",
            headers=auth_headers,
            json={"image_base64": b64},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "markers" in data
        assert isinstance(data["markers"], list)
        # at least the AI returned something parseable
        assert "raw_response" in data


# =========================================================================
# FOOD LABEL
# =========================================================================
class TestFoodLabel:
    def test_food_label_analyze(self, api_client, auth_headers):
        b64 = _make_label_image_b64()
        r = api_client.post(
            f"{BASE_URL}/api/food-label/analyze",
            headers=auth_headers,
            json={"image_base64": b64},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        # required keys
        for k in ("name", "protein_g", "salt_g", "calories", "sodium_mg"):
            assert k in data
        assert isinstance(data["protein_g"], (int, float))


# =========================================================================
# GOALS
# =========================================================================
class TestGoals:
    def test_goals_crud(self, api_client, auth_headers):
        wk = _monday()
        r = api_client.post(f"{BASE_URL}/api/goals", headers=auth_headers, json={"title": "TEST_goal", "week_start": wk})
        assert r.status_code == 200
        gid = r.json()["id"]
        assert r.json()["completed"] is False
        # list filtered
        r = api_client.get(f"{BASE_URL}/api/goals?week_start={wk}", headers=auth_headers)
        assert gid in [g["id"] for g in r.json()]
        # patch toggle
        r = api_client.patch(f"{BASE_URL}/api/goals/{gid}", headers=auth_headers, json={"completed": True})
        assert r.status_code == 200
        assert r.json()["completed"] is True
        # delete
        r = api_client.delete(f"{BASE_URL}/api/goals/{gid}", headers=auth_headers)
        assert r.status_code == 200


# =========================================================================
# GLOSSARY
# =========================================================================
class TestGlossary:
    def test_glossary_public(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/glossary")
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) >= 30
        sample = items[0]
        assert "term" in sample and "definition" in sample


# =========================================================================
# DASHBOARD
# =========================================================================
class TestDashboard:
    def test_dashboard_shape(self, api_client, auth_headers):
        r = api_client.get(f"{BASE_URL}/api/dashboard", headers=auth_headers)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "sobriety" in d and "today" in d and "goals" in d and "week_start" in d
        assert "totals" in d["today"]
        assert "targets" in d["today"]
        t = d["today"]["targets"]
        assert t["protein_g_min"] == 140
        assert t["salt_g_max"] == 2
        assert t["water_ml_max"] == 1500
        assert "weekly_rating_avg" in d
