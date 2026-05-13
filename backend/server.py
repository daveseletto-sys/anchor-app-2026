import os
import uuid
import logging
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


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    sobriety_start: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


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
