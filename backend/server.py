import os
import uuid
import logging
import secrets
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# Load env BEFORE importing modules that capture env vars at import time
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from auth import (  # noqa: E402
    hash_password,
    verify_password,
    create_token,
    get_current_user,
)
from llm_service import analyze_food_label, analyze_blood_test, generate_weekly_insight  # noqa: E402
from glossary_data import GLOSSARY  # noqa: E402
from hotlines_data import HOTLINES  # noqa: E402
from pdf_report import build_report_pdf  # noqa: E402
from fastapi.responses import Response  # noqa: E402
from email_service import (  # noqa: E402
    email_configured,
    send_email,
    doctor_report_html,
    weekly_digest_html,
)

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="Anchor Recovery API")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# -------- Models --------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AuthOut(BaseModel):
    token: str
    user: dict


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    sobriety_start: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    region: Optional[str] = None  # "US", "UK", or None
    created_at: str


class DiaryIn(BaseModel):
    date: str  # ISO date (YYYY-MM-DD)
    rating: int = Field(ge=1, le=10)
    mood_tags: List[str] = []
    notes: str = ""


class DiaryOut(DiaryIn):
    id: str
    created_at: str


class MealIn(BaseModel):
    date: str
    name: str
    protein_g: float = 0
    salt_g: float = 0
    water_ml: float = 0
    calories: float = 0
    notes: str = ""


class MealOut(MealIn):
    id: str
    created_at: str


class WaterIn(BaseModel):
    date: str
    amount_ml: float


class BloodTestMarker(BaseModel):
    name: str
    value: float
    unit: str = ""
    reference_range: str = ""


class BloodTestIn(BaseModel):
    date: str
    lab: str = ""
    markers: List[BloodTestMarker]
    notes: str = ""


class BloodTestOut(BloodTestIn):
    id: str
    created_at: str


class GoalIn(BaseModel):
    title: str
    week_start: str  # ISO date Monday of week
    completed: bool = False


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class GoalOut(GoalIn):
    id: str
    created_at: str


class SobrietyIn(BaseModel):
    sobriety_start: str  # ISO date


class FoodLabelIn(BaseModel):
    image_base64: str


class BloodExtractIn(BaseModel):
    image_base64: str


class ShareLinkCreate(BaseModel):
    expires_in_days: int = Field(default=7, ge=1, le=90)
    scope: str = Field(default="summary")  # "summary" | "full"


class ShareLinkOut(BaseModel):
    id: str
    token: str
    scope: str
    expires_at: str
    revoked: bool
    created_at: str


class ReportEmailIn(BaseModel):
    recipient_email: EmailStr
    period: str = "week"        # "week" | "month"
    scope: str = "clinical"     # "clinical" | "full" | "personal"
    note: Optional[str] = ""


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    sobriety_start: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    region: Optional[str] = None  # "US" or "UK"


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class MedicationIn(BaseModel):
    name: str
    dose: str = ""
    schedule: str = ""
    notes: str = ""
    active: bool = True


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dose: Optional[str] = None
    schedule: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class MedicationOut(MedicationIn):
    id: str
    created_at: str


class MedLogIn(BaseModel):
    medication_id: str
    date: str
    taken: bool = True


class MedLogOut(MedLogIn):
    id: str
    created_at: str


# -------- Helpers --------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


async def user_doc(user_id: str) -> dict:
    doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return doc


# -------- Auth --------

@api.post("/auth/register", response_model=AuthOut)
async def register(payload: RegisterIn):
    existing = await db.users.find_one({"email": payload.email.lower()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": payload.email.lower(),
        "name": payload.name,
        "password_hash": hash_password(payload.password),
        "sobriety_start": today_str(),
        "created_at": now_iso(),
    }
    await db.users.insert_one(user)
    token = create_token(user_id, user["email"])
    user.pop("password_hash", None)
    user.pop("_id", None)
    return {"token": token, "user": user}


@api.post("/auth/login", response_model=AuthOut)
async def login(payload: LoginIn):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user["id"], user["email"])
    user.pop("password_hash", None)
    user.pop("_id", None)
    return {"token": token, "user": user}


@api.get("/auth/me", response_model=UserOut)
async def me(current=Depends(get_current_user)):
    return await user_doc(current["id"])


# -------- Sobriety --------

@api.get("/sobriety")
async def get_sobriety(current=Depends(get_current_user)):
    u = await user_doc(current["id"])
    start = u.get("sobriety_start") or today_str()
    days = (datetime.now(timezone.utc).date() - date.fromisoformat(start)).days
    return {"sobriety_start": start, "days_sober": max(days, 0)}


@api.patch("/sobriety")
async def set_sobriety(payload: SobrietyIn, current=Depends(get_current_user)):
    # validate
    date.fromisoformat(payload.sobriety_start)
    await db.users.update_one({"id": current["id"]}, {"$set": {"sobriety_start": payload.sobriety_start}})
    days = (datetime.now(timezone.utc).date() - date.fromisoformat(payload.sobriety_start)).days
    return {"sobriety_start": payload.sobriety_start, "days_sober": max(days, 0)}


# -------- Diary --------

@api.get("/diary", response_model=List[DiaryOut])
async def list_diary(current=Depends(get_current_user)):
    items = await db.diary.find({"user_id": current["id"]}, {"_id": 0, "user_id": 0}).sort("date", -1).to_list(500)
    return items


@api.post("/diary", response_model=DiaryOut)
async def create_diary(payload: DiaryIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        "date": payload.date,
        "rating": payload.rating,
        "mood_tags": payload.mood_tags,
        "notes": payload.notes,
        "created_at": now_iso(),
    }
    await db.diary.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


@api.delete("/diary/{entry_id}")
async def delete_diary(entry_id: str, current=Depends(get_current_user)):
    res = await db.diary.delete_one({"id": entry_id, "user_id": current["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


# -------- Meals / Diet --------

@api.get("/meals", response_model=List[MealOut])
async def list_meals(date_str: Optional[str] = None, current=Depends(get_current_user)):
    q = {"user_id": current["id"]}
    if date_str:
        q["date"] = date_str
    items = await db.meals.find(q, {"_id": 0, "user_id": 0}).sort("created_at", -1).to_list(500)
    return items


@api.post("/meals", response_model=MealOut)
async def add_meal(payload: MealIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    await db.meals.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


@api.delete("/meals/{meal_id}")
async def delete_meal(meal_id: str, current=Depends(get_current_user)):
    res = await db.meals.delete_one({"id": meal_id, "user_id": current["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@api.get("/meals/totals")
async def meals_totals(date_str: Optional[str] = None, current=Depends(get_current_user)):
    d = date_str or today_str()
    items = await db.meals.find({"user_id": current["id"], "date": d}, {"_id": 0}).to_list(500)
    totals = {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0, "calories": 0.0}
    for it in items:
        totals["protein_g"] += float(it.get("protein_g") or 0)
        totals["salt_g"] += float(it.get("salt_g") or 0)
        totals["water_ml"] += float(it.get("water_ml") or 0)
        totals["calories"] += float(it.get("calories") or 0)
    return {"date": d, "totals": totals, "count": len(items)}


@api.post("/water")
async def quick_water(payload: WaterIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        "date": payload.date,
        "name": "Water",
        "protein_g": 0,
        "salt_g": 0,
        "water_ml": payload.amount_ml,
        "calories": 0,
        "notes": "",
        "created_at": now_iso(),
    }
    await db.meals.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


# -------- Blood Tests --------

@api.get("/blood-tests", response_model=List[BloodTestOut])
async def list_blood_tests(current=Depends(get_current_user)):
    items = await db.blood_tests.find({"user_id": current["id"]}, {"_id": 0, "user_id": 0}).sort("date", -1).to_list(500)
    return items


@api.post("/blood-tests", response_model=BloodTestOut)
async def add_blood_test(payload: BloodTestIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        "date": payload.date,
        "lab": payload.lab,
        "markers": [m.model_dump() for m in payload.markers],
        "notes": payload.notes,
        "created_at": now_iso(),
    }
    await db.blood_tests.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


@api.delete("/blood-tests/{test_id}")
async def delete_blood_test(test_id: str, current=Depends(get_current_user)):
    res = await db.blood_tests.delete_one({"id": test_id, "user_id": current["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@api.post("/blood-tests/extract")
async def extract_blood_test(payload: BloodExtractIn, current=Depends(get_current_user)):
    try:
        result = await analyze_blood_test(payload.image_base64)
        return result
    except Exception as e:
        logger.exception("blood test extract failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


# -------- Food Label --------

@api.post("/food-label/analyze")
async def analyze_food(payload: FoodLabelIn, current=Depends(get_current_user)):
    try:
        result = await analyze_food_label(payload.image_base64)
        return result
    except Exception as e:
        logger.exception("food label analyze failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# -------- Goals --------

@api.get("/goals", response_model=List[GoalOut])
async def list_goals(week_start: Optional[str] = None, current=Depends(get_current_user)):
    q = {"user_id": current["id"]}
    if week_start:
        q["week_start"] = week_start
    items = await db.goals.find(q, {"_id": 0, "user_id": 0}).sort("created_at", 1).to_list(500)
    return items


@api.post("/goals", response_model=GoalOut)
async def add_goal(payload: GoalIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    await db.goals.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


@api.patch("/goals/{goal_id}", response_model=GoalOut)
async def update_goal(goal_id: str, payload: GoalUpdate, current=Depends(get_current_user)):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No changes")
    res = await db.goals.update_one({"id": goal_id, "user_id": current["id"]}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    doc = await db.goals.find_one({"id": goal_id}, {"_id": 0, "user_id": 0})
    return doc


@api.delete("/goals/{goal_id}")
async def delete_goal(goal_id: str, current=Depends(get_current_user)):
    res = await db.goals.delete_one({"id": goal_id, "user_id": current["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


# -------- Glossary --------

@api.get("/glossary")
async def glossary():
    return {"items": GLOSSARY}


# -------- Dashboard --------

@api.get("/dashboard")
async def dashboard(current=Depends(get_current_user)):
    u = await user_doc(current["id"])
    start = u.get("sobriety_start") or today_str()
    days = (datetime.now(timezone.utc).date() - date.fromisoformat(start)).days
    d = today_str()

    meals = await db.meals.find({"user_id": current["id"], "date": d}, {"_id": 0}).to_list(500)
    totals = {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0, "calories": 0.0}
    for it in meals:
        totals["protein_g"] += float(it.get("protein_g") or 0)
        totals["salt_g"] += float(it.get("salt_g") or 0)
        totals["water_ml"] += float(it.get("water_ml") or 0)
        totals["calories"] += float(it.get("calories") or 0)

    today_entry = await db.diary.find_one({"user_id": current["id"], "date": d}, {"_id": 0, "user_id": 0})

    # weekly diary average (last 7 days)
    week_ago = (datetime.now(timezone.utc).date() - timedelta(days=7)).isoformat()
    week_entries = await db.diary.find(
        {"user_id": current["id"], "date": {"$gte": week_ago}}, {"_id": 0, "rating": 1, "date": 1}
    ).to_list(50)
    weekly_avg = round(sum(e["rating"] for e in week_entries) / len(week_entries), 1) if week_entries else None

    # this week's goals
    today_dt = datetime.now(timezone.utc).date()
    monday = today_dt - timedelta(days=today_dt.weekday())
    goals = await db.goals.find(
        {"user_id": current["id"], "week_start": monday.isoformat()}, {"_id": 0, "user_id": 0}
    ).to_list(100)

    return {
        "sobriety": {"sobriety_start": start, "days_sober": max(days, 0)},
        "today": {
            "date": d,
            "totals": totals,
            "diary": today_entry,
            "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
        },
        "weekly_rating_avg": weekly_avg,
        "goals": goals,
        "week_start": monday.isoformat(),
    }


@api.get("/")
async def root():
    return {"message": "Anchor Recovery API", "ok": True}


# -------- Profile --------

@api.patch("/users/me", response_model=UserOut)
async def update_profile(payload: ProfileUpdate, current=Depends(get_current_user)):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "sobriety_start" in update:
        try:
            date.fromisoformat(update["sobriety_start"])
        except ValueError:
            raise HTTPException(status_code=422, detail="sobriety_start must be ISO date YYYY-MM-DD")
    if "region" in update and update["region"] not in (None, "", "US", "UK"):
        raise HTTPException(status_code=422, detail="region must be 'US', 'UK', or null")
    if not update:
        raise HTTPException(status_code=400, detail="No changes")
    await db.users.update_one({"id": current["id"]}, {"$set": update})
    return await user_doc(current["id"])


@api.post("/auth/change-password")
async def change_password(payload: PasswordChange, current=Depends(get_current_user)):
    user = await db.users.find_one({"id": current["id"]})
    if not user or not verify_password(payload.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    await db.users.update_one(
        {"id": current["id"]},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    return {"ok": True}


# -------- Medications --------

@api.get("/medications", response_model=List[MedicationOut])
async def list_medications(current=Depends(get_current_user)):
    items = await db.medications.find(
        {"user_id": current["id"]}, {"_id": 0, "user_id": 0}
    ).sort("created_at", 1).to_list(500)
    return items


@api.post("/medications", response_model=MedicationOut)
async def add_medication(payload: MedicationIn, current=Depends(get_current_user)):
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    await db.medications.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


@api.patch("/medications/{med_id}", response_model=MedicationOut)
async def update_medication(med_id: str, payload: MedicationUpdate, current=Depends(get_current_user)):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No changes")
    res = await db.medications.update_one({"id": med_id, "user_id": current["id"]}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    doc = await db.medications.find_one({"id": med_id}, {"_id": 0, "user_id": 0})
    return doc


@api.delete("/medications/{med_id}")
async def delete_medication(med_id: str, current=Depends(get_current_user)):
    res = await db.medications.delete_one({"id": med_id, "user_id": current["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    # also clean logs
    await db.med_logs.delete_many({"medication_id": med_id, "user_id": current["id"]})
    return {"ok": True}


@api.get("/medications/log", response_model=List[MedLogOut])
async def list_med_logs(date_str: Optional[str] = None, current=Depends(get_current_user)):
    q = {"user_id": current["id"]}
    if date_str:
        q["date"] = date_str
    items = await db.med_logs.find(q, {"_id": 0, "user_id": 0}).to_list(500)
    return items


@api.post("/medications/log", response_model=MedLogOut)
async def add_med_log(payload: MedLogIn, current=Depends(get_current_user)):
    # upsert: one log per (med, date)
    existing = await db.med_logs.find_one(
        {"user_id": current["id"], "medication_id": payload.medication_id, "date": payload.date}
    )
    if existing:
        await db.med_logs.update_one(
            {"id": existing["id"]}, {"$set": {"taken": payload.taken}}
        )
        existing["taken"] = payload.taken
        existing.pop("user_id", None)
        existing.pop("_id", None)
        return existing
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    await db.med_logs.insert_one(entry)
    entry.pop("user_id", None)
    entry.pop("_id", None)
    return entry


# -------- Weekly Insight --------

@api.post("/insights/weekly")
async def weekly_insight(current=Depends(get_current_user)):
    user = await user_doc(current["id"])
    today_dt = datetime.now(timezone.utc).date()
    monday = today_dt - timedelta(days=today_dt.weekday())
    week_start = monday.isoformat()

    # Return cached if it exists (regenerated on demand)
    cached = await db.weekly_insights.find_one(
        {"user_id": current["id"], "week_start": week_start}, {"_id": 0, "user_id": 0}
    )

    # Build context
    seven_days_ago = (today_dt - timedelta(days=7)).isoformat()
    diary = await db.diary.find(
        {"user_id": current["id"], "date": {"$gte": seven_days_ago}}, {"_id": 0, "user_id": 0}
    ).sort("date", 1).to_list(50)
    meals = await db.meals.find(
        {"user_id": current["id"], "date": {"$gte": seven_days_ago}}, {"_id": 0}
    ).to_list(500)

    # Aggregate diet
    by_day = {}
    for m in meals:
        d = m.get("date")
        by_day.setdefault(d, {"protein_g": 0, "salt_g": 0, "water_ml": 0, "calories": 0})
        by_day[d]["protein_g"] += float(m.get("protein_g") or 0)
        by_day[d]["salt_g"] += float(m.get("salt_g") or 0)
        by_day[d]["water_ml"] += float(m.get("water_ml") or 0)
        by_day[d]["calories"] += float(m.get("calories") or 0)

    diet_summary = {
        "days_logged": len(by_day),
        "avg_protein_g": round(sum(d["protein_g"] for d in by_day.values()) / max(len(by_day), 1), 1),
        "avg_salt_g": round(sum(d["salt_g"] for d in by_day.values()) / max(len(by_day), 1), 2),
        "avg_water_ml": round(sum(d["water_ml"] for d in by_day.values()) / max(len(by_day), 1), 0),
        "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
    }

    # Med adherence
    meds = await db.medications.find(
        {"user_id": current["id"], "active": True}, {"_id": 0, "user_id": 0}
    ).to_list(100)
    logs = await db.med_logs.find(
        {"user_id": current["id"], "date": {"$gte": seven_days_ago}}, {"_id": 0, "user_id": 0}
    ).to_list(500)
    taken_count = sum(1 for log in logs if log.get("taken"))
    expected = len(meds) * 7
    adherence = f"{taken_count}/{expected}" if expected else "n/a"

    # Goals
    goals = await db.goals.find(
        {"user_id": current["id"], "week_start": week_start}, {"_id": 0, "user_id": 0}
    ).to_list(100)
    goals_done = sum(1 for g in goals if g.get("completed"))

    # Sobriety
    sob_start = user.get("sobriety_start") or today_str()
    days_sober = max((today_dt - date.fromisoformat(sob_start)).days, 0)

    context = {
        "name": user.get("name", "friend"),
        "week_label": f"{seven_days_ago} to {today_dt.isoformat()}",
        "days_sober": days_sober,
        "diary_entries": [
            {"date": d.get("date"), "rating": d.get("rating"), "mood_tags": d.get("mood_tags", []), "notes": (d.get("notes") or "")[:280]}
            for d in diary
        ],
        "diet_summary": diet_summary,
        "medication_adherence": adherence,
        "medications": [m.get("name") for m in meds],
        "goals_done": goals_done,
        "goals_total": len(goals),
        "goals_titles": [g.get("title") for g in goals],
    }

    try:
        text = await generate_weekly_insight(context)
    except Exception as e:
        logger.exception("weekly insight failed")
        if cached:
            return {"week_start": week_start, "text": cached.get("text", ""), "stale": True}
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

    payload = {
        "user_id": current["id"],
        "week_start": week_start,
        "text": text,
        "context": context,
        "created_at": now_iso(),
    }
    await db.weekly_insights.update_one(
        {"user_id": current["id"], "week_start": week_start},
        {"$set": payload},
        upsert=True,
    )
    return {"week_start": week_start, "text": text, "stale": False}


@api.get("/insights/weekly")
async def get_weekly_insight(current=Depends(get_current_user)):
    today_dt = datetime.now(timezone.utc).date()
    monday = today_dt - timedelta(days=today_dt.weekday())
    week_start = monday.isoformat()
    cached = await db.weekly_insights.find_one(
        {"user_id": current["id"], "week_start": week_start}, {"_id": 0, "user_id": 0}
    )
    if not cached:
        return {"week_start": week_start, "text": None}
    return {"week_start": week_start, "text": cached.get("text", ""), "created_at": cached.get("created_at")}


# -------- Crisis / Hotlines --------

@api.get("/crisis")
async def get_crisis_lines(current=Depends(get_current_user)):
    user = await user_doc(current["id"])
    region = user.get("region")
    if region in ("US", "UK"):
        return {"region": region, "regions": [region], "hotlines": HOTLINES[region]}
    # both
    return {
        "region": None,
        "regions": ["US", "UK"],
        "hotlines": {"US": HOTLINES["US"], "UK": HOTLINES["UK"]},
    }


# -------- Reports / PDF Export --------

async def _generate_report_pdf(user_id: str, period: str, scope: str) -> tuple[bytes, str, str]:
    """Return (pdf_bytes, filename, period_label) for the given user."""
    if period not in ("week", "month"):
        raise HTTPException(status_code=422, detail="period must be 'week' or 'month'")
    if scope not in ("clinical", "full", "personal"):
        raise HTTPException(status_code=422, detail="scope must be 'clinical', 'full', or 'personal'")

    user = await user_doc(user_id)
    today_dt = datetime.now(timezone.utc).date()
    days = 7 if period == "week" else 30
    start_dt = today_dt - timedelta(days=days - 1)
    period_label = "Last 7 days" if period == "week" else "Last 30 days"
    start_iso = start_dt.isoformat()

    sob_start = user.get("sobriety_start") or today_str()
    days_sober = max((today_dt - date.fromisoformat(sob_start)).days, 0)

    meals = await db.meals.find(
        {"user_id": user_id, "date": {"$gte": start_iso}}, {"_id": 0}
    ).to_list(2000)
    by_day = {}
    for m in meals:
        d = m.get("date")
        by_day.setdefault(d, {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0, "calories": 0.0})
        by_day[d]["protein_g"] += float(m.get("protein_g") or 0)
        by_day[d]["salt_g"] += float(m.get("salt_g") or 0)
        by_day[d]["water_ml"] += float(m.get("water_ml") or 0)
        by_day[d]["calories"] += float(m.get("calories") or 0)
    days_logged = len(by_day)
    diet_summary = {
        "days_logged": days_logged,
        "avg_protein_g": round(sum(d["protein_g"] for d in by_day.values()) / max(days_logged, 1), 1),
        "avg_salt_g": round(sum(d["salt_g"] for d in by_day.values()) / max(days_logged, 1), 2),
        "avg_water_ml": round(sum(d["water_ml"] for d in by_day.values()) / max(days_logged, 1), 0),
        "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
    }
    protein_ok = sum(1 for d in by_day.values() if d["protein_g"] >= 140)
    salt_ok = sum(1 for d in by_day.values() if d["salt_g"] <= 2)
    water_ok = sum(1 for d in by_day.values() if d["water_ml"] <= 1500)
    diet_compliance = {
        "protein_pct": round(protein_ok / max(days_logged, 1) * 100),
        "salt_pct": round(salt_ok / max(days_logged, 1) * 100),
        "water_pct": round(water_ok / max(days_logged, 1) * 100),
    }

    blood = await db.blood_tests.find(
        {"user_id": user_id, "date": {"$gte": start_iso}}, {"_id": 0, "user_id": 0}
    ).sort("date", 1).to_list(200)

    meds = await db.medications.find(
        {"user_id": user_id}, {"_id": 0, "user_id": 0}
    ).to_list(200)
    logs = await db.med_logs.find(
        {"user_id": user_id, "date": {"$gte": start_iso}}, {"_id": 0, "user_id": 0}
    ).to_list(2000)
    adherence = {}
    for m in meds:
        if not m.get("active"):
            adherence[m["id"]] = {"taken": 0, "expected": 0}
            continue
        expected = days
        taken = sum(1 for log in logs if log.get("medication_id") == m["id"] and log.get("taken"))
        adherence[m["id"]] = {"taken": taken, "expected": expected}

    goals = await db.goals.find(
        {"user_id": user_id, "week_start": {"$gte": (start_dt - timedelta(days=6)).isoformat()}},
        {"_id": 0, "user_id": 0},
    ).sort("week_start", 1).to_list(200)

    diary = await db.diary.find(
        {"user_id": user_id, "date": {"$gte": start_iso}}, {"_id": 0, "user_id": 0}
    ).sort("date", 1).to_list(200)
    diary_avg = round(sum(e["rating"] for e in diary) / len(diary), 1) if diary else None

    pdf_bytes = build_report_pdf(
        user=user,
        period_label=period_label,
        start_date=start_dt,
        end_date=today_dt,
        days_sober=days_sober,
        scope=scope,
        diet_summary=diet_summary,
        diet_compliance=diet_compliance,
        blood_tests=blood,
        medications=meds,
        medication_adherence=adherence,
        goals=goals,
        diary=diary if scope in ("full", "personal") else [],
        diary_avg_rating=diary_avg if scope in ("full", "personal") else None,
    )

    filename = f"anchor-report-{user.get('name','user').replace(' ', '-').lower()}-{today_dt.isoformat()}-{period}-{scope}.pdf"
    return pdf_bytes, filename, period_label


@api.get("/reports/pdf")
async def reports_pdf(
    period: str = "week",
    scope: str = "clinical",
    current=Depends(get_current_user),
):
    pdf_bytes, filename, _ = await _generate_report_pdf(current["id"], period, scope)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# -------- Correlations (mood vs diet) --------

@api.get("/correlations")
async def correlations(days: int = 30, current=Depends(get_current_user)):
    if days < 1 or days > 180:
        raise HTTPException(status_code=422, detail="days must be 1..180")
    today_dt = datetime.now(timezone.utc).date()
    start_dt = today_dt - timedelta(days=days - 1)
    start_iso = start_dt.isoformat()

    # Diary by date
    diary_rows = await db.diary.find(
        {"user_id": current["id"], "date": {"$gte": start_iso}},
        {"_id": 0, "user_id": 0},
    ).to_list(2000)
    diary_by_date = {d["date"]: d for d in diary_rows}

    # Diet totals by date
    meals = await db.meals.find(
        {"user_id": current["id"], "date": {"$gte": start_iso}}, {"_id": 0}
    ).to_list(5000)
    diet_by_date = {}
    for m in meals:
        d = m.get("date")
        diet_by_date.setdefault(d, {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0, "calories": 0.0})
        diet_by_date[d]["protein_g"] += float(m.get("protein_g") or 0)
        diet_by_date[d]["salt_g"] += float(m.get("salt_g") or 0)
        diet_by_date[d]["water_ml"] += float(m.get("water_ml") or 0)
        diet_by_date[d]["calories"] += float(m.get("calories") or 0)

    # Build series for every day in range
    series = []
    for i in range(days):
        d = (start_dt + timedelta(days=i)).isoformat()
        diary = diary_by_date.get(d)
        diet = diet_by_date.get(d, {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0, "calories": 0.0})
        series.append({
            "date": d,
            "rating": diary.get("rating") if diary else None,
            "protein_g": round(diet["protein_g"], 1),
            "salt_g": round(diet["salt_g"], 2),
            "water_ml": round(diet["water_ml"], 0),
        })

    # Pearson correlation between rating and each diet metric (only days with both)
    def corr(xs, ys):
        n = len(xs)
        if n < 3:
            return None
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        if dx == 0 or dy == 0:
            return None
        return round(num / (dx * dy), 2)

    paired = [(s["rating"], s["protein_g"], s["salt_g"], s["water_ml"]) for s in series if s["rating"] is not None]
    correlations_out = {
        "protein": corr([p[0] for p in paired], [p[1] for p in paired]) if paired else None,
        "salt": corr([p[0] for p in paired], [p[2] for p in paired]) if paired else None,
        "water": corr([p[0] for p in paired], [p[3] for p in paired]) if paired else None,
        "n": len(paired),
    }

    return {"days": days, "series": series, "correlations": correlations_out}


# -------- Share Links (sponsor read-only) --------

@api.post("/share-links", response_model=ShareLinkOut)
async def create_share_link(payload: ShareLinkCreate, current=Depends(get_current_user)):
    if payload.scope not in ("summary", "full"):
        raise HTTPException(status_code=422, detail="scope must be 'summary' or 'full'")
    token = secrets.token_urlsafe(24)
    expires = datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days)
    doc = {
        "id": str(uuid.uuid4()),
        "user_id": current["id"],
        "token": token,
        "scope": payload.scope,
        "expires_at": expires.isoformat(),
        "revoked": False,
        "created_at": now_iso(),
    }
    await db.share_links.insert_one(doc)
    doc.pop("user_id", None)
    doc.pop("_id", None)
    return doc


@api.get("/share-links", response_model=List[ShareLinkOut])
async def list_share_links(current=Depends(get_current_user)):
    items = await db.share_links.find(
        {"user_id": current["id"]}, {"_id": 0, "user_id": 0}
    ).sort("created_at", -1).to_list(100)
    return items


@api.delete("/share-links/{link_id}")
async def revoke_share_link(link_id: str, current=Depends(get_current_user)):
    res = await db.share_links.update_one(
        {"id": link_id, "user_id": current["id"]},
        {"$set": {"revoked": True}},
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@api.get("/shared/{token}")
async def view_shared(token: str):
    link = await db.share_links.find_one({"token": token}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.get("revoked"):
        raise HTTPException(status_code=410, detail="Link revoked")
    try:
        exp = datetime.fromisoformat(link["expires_at"])
    except Exception:
        raise HTTPException(status_code=410, detail="Invalid link")
    if datetime.now(timezone.utc) > exp:
        raise HTTPException(status_code=410, detail="Link expired")

    user = await db.users.find_one({"id": link["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Owner not found")

    today_dt = datetime.now(timezone.utc).date()
    sob_start = user.get("sobriety_start") or today_dt.isoformat()
    days_sober = max((today_dt - date.fromisoformat(sob_start)).days, 0)

    # Last 7 days summary
    week_ago = (today_dt - timedelta(days=6)).isoformat()
    meals = await db.meals.find(
        {"user_id": link["user_id"], "date": {"$gte": week_ago}}, {"_id": 0}
    ).to_list(2000)
    by_day = {}
    for m in meals:
        d = m.get("date")
        by_day.setdefault(d, {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0})
        by_day[d]["protein_g"] += float(m.get("protein_g") or 0)
        by_day[d]["salt_g"] += float(m.get("salt_g") or 0)
        by_day[d]["water_ml"] += float(m.get("water_ml") or 0)
    days_logged = len(by_day)
    diet_summary = {
        "days_logged": days_logged,
        "avg_protein_g": round(sum(d["protein_g"] for d in by_day.values()) / max(days_logged, 1), 1),
        "avg_salt_g": round(sum(d["salt_g"] for d in by_day.values()) / max(days_logged, 1), 2),
        "avg_water_ml": round(sum(d["water_ml"] for d in by_day.values()) / max(days_logged, 1), 0),
        "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
    }

    diary_rows = await db.diary.find(
        {"user_id": link["user_id"], "date": {"$gte": week_ago}}, {"_id": 0, "user_id": 0}
    ).sort("date", -1).to_list(20)
    diary_avg = round(sum(e["rating"] for e in diary_rows) / len(diary_rows), 1) if diary_rows else None

    today_mon = today_dt - timedelta(days=today_dt.weekday())
    goals = await db.goals.find(
        {"user_id": link["user_id"], "week_start": today_mon.isoformat()},
        {"_id": 0, "user_id": 0},
    ).to_list(50)

    return {
        "owner_name": user.get("name", ""),
        "expires_at": link["expires_at"],
        "scope": link.get("scope", "summary"),
        "sobriety": {"days_sober": days_sober, "sobriety_start": sob_start},
        "diet_summary": diet_summary,
        "diary_avg_rating": diary_avg,
        "goals": [{"title": g.get("title"), "completed": g.get("completed", False)} for g in goals],
        "diary_entries": (
            [
                {"date": e.get("date"), "rating": e.get("rating"), "mood_tags": e.get("mood_tags", [])}
                for e in diary_rows
            ]
            if link.get("scope") == "full" else []
        ),
    }


# -------- Email: send report to doctor --------

@api.post("/reports/email")
async def email_report(payload: ReportEmailIn, current=Depends(get_current_user)):
    if not email_configured():
        raise HTTPException(status_code=503, detail="Email service is not configured. Add RESEND_API_KEY.")
    pdf_bytes, filename, period_label = await _generate_report_pdf(current["id"], payload.period, payload.scope)
    user = await user_doc(current["id"])
    html = doctor_report_html(
        sender_name=user.get("name", "An Anchor user"),
        period_label=period_label,
        personal_note=(payload.note or "").strip(),
    )
    subject = f"{user.get('name','An Anchor user')}'s recovery report — {period_label}"
    try:
        result = await send_email(
            to=str(payload.recipient_email),
            subject=subject,
            html=html,
            reply_to=user.get("email"),
            attachment_bytes=pdf_bytes,
            attachment_filename=filename,
        )
        return {"ok": True, "email_id": result.get("id") if isinstance(result, dict) else None}
    except Exception as e:
        logger.exception("send report email failed")
        msg = str(e)
        if "only send testing emails" in msg.lower() or "verify a domain" in msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Resend is in test mode — emails can only go to the email tied to your Resend account. To send to your doctor (or any other address), verify a domain at resend.com/domains and update SENDER_EMAIL in /app/backend/.env.",
            )
        raise HTTPException(status_code=502, detail=f"Email send failed: {msg}")


# -------- Email: weekly insight digest --------

@api.post("/insights/email-digest")
async def email_weekly_digest(current=Depends(get_current_user)):
    if not email_configured():
        raise HTTPException(status_code=503, detail="Email service is not configured. Add RESEND_API_KEY.")
    user = await user_doc(current["id"])

    today_dt = datetime.now(timezone.utc).date()
    monday = today_dt - timedelta(days=today_dt.weekday())
    week_start = monday.isoformat()

    cached = await db.weekly_insights.find_one(
        {"user_id": current["id"], "week_start": week_start}, {"_id": 0, "user_id": 0}
    )
    if not cached or not (cached.get("text") or "").strip():
        raise HTTPException(status_code=400, detail="No insight for this week yet — generate one first on the Dashboard.")

    sob_start = user.get("sobriety_start") or today_dt.isoformat()
    days_sober = max((today_dt - date.fromisoformat(sob_start)).days, 0)
    week_label = f"Week of {monday.strftime('%b %d, %Y')}"

    html = weekly_digest_html(
        name=user.get("name", "friend"),
        days_sober=days_sober,
        insight_text=cached["text"],
        week_label=week_label,
    )
    try:
        result = await send_email(
            to=user["email"],
            subject=f"This week — {user.get('name','friend')}",
            html=html,
        )
        return {"ok": True, "email_id": result.get("id") if isinstance(result, dict) else None}
    except Exception as e:
        logger.exception("send digest email failed")
        msg = str(e)
        if "only send testing emails" in msg.lower() or "verify a domain" in msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Resend is in test mode — your account email is not verified with Resend so we can't email this digest to you yet. Update your account email in Anchor to match your Resend account, or verify a domain at resend.com/domains.",
            )
        raise HTTPException(status_code=502, detail=f"Email send failed: {msg}")


# -------- Milestones (personal records, no ranking) --------

@api.get("/milestones")
async def milestones(current=Depends(get_current_user)):
    user = await user_doc(current["id"])
    today_dt = datetime.now(timezone.utc).date()
    sob_start = user.get("sobriety_start") or today_dt.isoformat()
    days_sober = max((today_dt - date.fromisoformat(sob_start)).days, 0)

    # Aggregate per-day diet totals (whole history)
    meals = await db.meals.find({"user_id": current["id"]}, {"_id": 0}).to_list(50000)
    by_day = {}
    for m in meals:
        d = m.get("date")
        by_day.setdefault(d, {"protein_g": 0.0, "salt_g": 0.0, "water_ml": 0.0})
        by_day[d]["protein_g"] += float(m.get("protein_g") or 0)
        by_day[d]["salt_g"] += float(m.get("salt_g") or 0)
        by_day[d]["water_ml"] += float(m.get("water_ml") or 0)

    # Best single day
    best_protein_day = max(by_day.items(), key=lambda kv: kv[1]["protein_g"], default=(None, {"protein_g": 0}))
    # Compliance streak (consecutive days hitting protein target)
    sorted_days = sorted(by_day.keys())
    best_streak = 0
    cur_streak = 0
    prev = None
    for d in sorted_days:
        if by_day[d]["protein_g"] >= 140:
            if prev is None or (date.fromisoformat(d) - date.fromisoformat(prev)).days == 1:
                cur_streak += 1
            else:
                cur_streak = 1
            best_streak = max(best_streak, cur_streak)
            prev = d
        else:
            cur_streak = 0
            prev = d
    days_meeting_protein = sum(1 for v in by_day.values() if v["protein_g"] >= 140)
    days_within_salt = sum(1 for v in by_day.values() if v["salt_g"] <= 2 and v["salt_g"] > 0)
    days_logged = len(by_day)

    # Diary milestones
    diary = await db.diary.find({"user_id": current["id"]}, {"_id": 0, "user_id": 0}).to_list(50000)
    diary_count = len(diary)
    best_rating_day = max(diary, key=lambda e: e.get("rating", 0), default=None)
    avg_rating = round(sum(e["rating"] for e in diary) / len(diary), 1) if diary else None
    # Best 7-day rolling average mood
    by_diary_date = {e["date"]: e.get("rating", 0) for e in diary}
    best_7d_avg = None
    best_7d_window = None
    if diary:
        dates = sorted(by_diary_date.keys())
        for d in dates:
            d_dt = date.fromisoformat(d)
            window = [by_diary_date.get((d_dt - timedelta(days=i)).isoformat()) for i in range(7)]
            window = [v for v in window if v is not None]
            if len(window) >= 4:  # need at least 4 days in window to count
                avg = round(sum(window) / len(window), 1)
                if best_7d_avg is None or avg > best_7d_avg:
                    best_7d_avg = avg
                    best_7d_window = d

    # Medication adherence (last 30 days)
    meds = await db.medications.find({"user_id": current["id"], "active": True}, {"_id": 0}).to_list(100)
    week_ago = (today_dt - timedelta(days=29)).isoformat()
    logs = await db.med_logs.find(
        {"user_id": current["id"], "date": {"$gte": week_ago}}, {"_id": 0}
    ).to_list(5000)
    expected = len(meds) * 30
    taken = sum(1 for log in logs if log.get("taken"))
    med_adherence_pct = round(taken / expected * 100) if expected else None

    # Goals completed
    all_goals = await db.goals.find({"user_id": current["id"]}, {"_id": 0}).to_list(5000)
    goals_completed = sum(1 for g in all_goals if g.get("completed"))

    return {
        "current_streak_days": days_sober,
        "best_protein_day": (
            {"date": best_protein_day[0], "protein_g": round(best_protein_day[1]["protein_g"], 1)}
            if best_protein_day[0] else None
        ),
        "best_protein_streak": best_streak,
        "days_meeting_protein": days_meeting_protein,
        "days_within_salt": days_within_salt,
        "diet_days_logged": days_logged,
        "diary_entries": diary_count,
        "avg_rating_all_time": avg_rating,
        "best_rating_day": (
            {"date": best_rating_day.get("date"), "rating": best_rating_day.get("rating")}
            if best_rating_day else None
        ),
        "best_7d_mood_avg": best_7d_avg,
        "best_7d_window_end": best_7d_window,
        "med_adherence_30d_pct": med_adherence_pct,
        "goals_completed": goals_completed,
    }


# -------- Community averages (anonymous, no ranking) --------

@api.get("/community/averages")
async def community_averages(current=Depends(get_current_user)):
    today_dt = datetime.now(timezone.utc).date()
    month_ago = (today_dt - timedelta(days=29)).isoformat()
    # Aggregate diet across ALL users (anonymous)
    pipeline = [
        {"$match": {"date": {"$gte": month_ago}}},
        {"$group": {
            "_id": {"user": "$user_id", "date": "$date"},
            "protein_g": {"$sum": "$protein_g"},
            "salt_g": {"$sum": "$salt_g"},
            "water_ml": {"$sum": "$water_ml"},
        }},
        {"$group": {
            "_id": None,
            "avg_protein_g": {"$avg": "$protein_g"},
            "avg_salt_g": {"$avg": "$salt_g"},
            "avg_water_ml": {"$avg": "$water_ml"},
            "user_days": {"$sum": 1},
            "unique_users": {"$addToSet": "$_id.user"},
        }},
    ]
    res = await db.meals.aggregate(pipeline).to_list(1)
    if not res:
        return {
            "users_count": 0,
            "user_days": 0,
            "avg_protein_g": None,
            "avg_salt_g": None,
            "avg_water_ml": None,
            "avg_mood": None,
            "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
            "min_users_threshold": 5,
        }
    row = res[0]
    unique_users = len(row.get("unique_users") or [])

    # Community mood avg (last 30 days)
    mood_pipe = [
        {"$match": {"date": {"$gte": month_ago}}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "users": {"$addToSet": "$user_id"}}},
    ]
    mood_res = await db.diary.aggregate(mood_pipe).to_list(1)
    avg_mood = round(mood_res[0]["avg_rating"], 1) if mood_res else None

    # Privacy guard: only return if we have at least 5 users in aggregate
    if unique_users < 5:
        return {
            "users_count": unique_users,
            "user_days": row.get("user_days", 0),
            "avg_protein_g": None,
            "avg_salt_g": None,
            "avg_water_ml": None,
            "avg_mood": None,
            "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
            "min_users_threshold": 5,
        }

    return {
        "users_count": unique_users,
        "user_days": row.get("user_days", 0),
        "avg_protein_g": round(row["avg_protein_g"], 1) if row.get("avg_protein_g") is not None else None,
        "avg_salt_g": round(row["avg_salt_g"], 2) if row.get("avg_salt_g") is not None else None,
        "avg_water_ml": round(row["avg_water_ml"], 0) if row.get("avg_water_ml") is not None else None,
        "avg_mood": avg_mood,
        "targets": {"protein_g_min": 140, "salt_g_max": 2, "water_ml_max": 1500},
        "min_users_threshold": 5,
    }


app.include_router(api)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
