# Anchor Recovery — API Contract

> Stable contract for the Anchor Recovery API. **The mobile app (and any other client) MUST follow this contract exactly.** Do not invent endpoints or fields. If something is missing, request it from the backend team rather than reimplementing.

**Base URL (production):** `https://progress-hub-256.emergent.host/api`
**Base URL (preview/dev):** value of `REACT_APP_BACKEND_URL` env var + `/api`
**API version:** `1.0.0` (check `GET /api/version`)

---

## Authentication

JWT (HS256) email + password. Token returned at register / login. Send on every authenticated request:

```
Authorization: Bearer <token>
```

Token expires in 30 days. On 401, force the user to log in again.

---

## Endpoints

### Public (no auth)

| Method | Path | Description |
|---|---|---|
| GET | `/api/` | Liveness check. Returns `{message, ok:true}` |
| GET | `/api/version` | Compatibility check. Returns `{api_version, min_mobile_client_version, name, ok}` |
| GET | `/api/glossary` | Returns `{items: [{term, definition}]}` (31 curated terms) |
| GET | `/api/shared/{token}` | Public read-only view of a share link. 404 if not found, 410 if revoked or expired |

### Auth

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/auth/register` | `{email, password (≥6), name}` | `{token, user}` |
| POST | `/api/auth/login` | `{email, password}` | `{token, user}` |
| GET | `/api/auth/me` | — | `UserOut` |
| POST | `/api/auth/change-password` | `{current_password, new_password (≥6)}` | `{ok:true}` |

### Profile

| Method | Path | Body | Returns |
|---|---|---|---|
| PATCH | `/api/users/me` | `{name?, sobriety_start? (ISO date), height_cm?, weight_kg?, region? ("US"\|"UK"\|"")}` | `UserOut` |

### Sobriety

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/api/sobriety` | — | `{sobriety_start, days_sober}` |
| PATCH | `/api/sobriety` | `{sobriety_start}` | `{sobriety_start, days_sober}` |

### Diary

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/api/diary` | — | `[DiaryOut]` (sorted date desc) |
| POST | `/api/diary` | `DiaryIn` | `DiaryOut` |
| DELETE | `/api/diary/{id}` | — | `{ok:true}` |

### Meals / Diet

| Method | Path | Query | Body | Returns |
|---|---|---|---|---|
| GET | `/api/meals` | `date_str?` (YYYY-MM-DD) | — | `[MealOut]` |
| POST | `/api/meals` | — | `MealIn` | `MealOut` |
| DELETE | `/api/meals/{id}` | — | — | `{ok:true}` |
| GET | `/api/meals/totals` | `date_str?` | — | `{date, totals: {protein_g, salt_g, water_ml, calories}, count}` |
| POST | `/api/water` | — | `{date, amount_ml}` | `MealOut` (entry with name="Water") |

### Blood Tests

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/api/blood-tests` | — | `[BloodTestOut]` |
| POST | `/api/blood-tests` | `BloodTestIn` | `BloodTestOut` |
| DELETE | `/api/blood-tests/{id}` | — | `{ok:true}` |
| POST | `/api/blood-tests/extract` | `{image_base64}` | `{date, lab, markers: [BloodTestMarker], notes, raw_response}` |

### Food Label

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/food-label/analyze` | `{image_base64}` | `{name, serving_size, calories, protein_g, salt_g, sodium_mg, sugar_g, fat_g, notes, raw_response}` |

### Goals

| Method | Path | Query | Body | Returns |
|---|---|---|---|---|
| GET | `/api/goals` | `week_start?` (ISO Monday) | — | `[GoalOut]` |
| POST | `/api/goals` | — | `{title, week_start, completed?}` | `GoalOut` |
| PATCH | `/api/goals/{id}` | — | `{title?, completed?}` | `GoalOut` |
| DELETE | `/api/goals/{id}` | — | — | `{ok:true}` |

### Medications

| Method | Path | Query | Body | Returns |
|---|---|---|---|---|
| GET | `/api/medications` | — | — | `[MedicationOut]` |
| POST | `/api/medications` | — | `MedicationIn` | `MedicationOut` |
| PATCH | `/api/medications/{id}` | — | `MedicationUpdate` | `MedicationOut` |
| DELETE | `/api/medications/{id}` | — | — | `{ok:true}` (cascades med_logs) |
| GET | `/api/medications/log` | `date_str?` | — | `[MedLogOut]` |
| POST | `/api/medications/log` | — | `{medication_id, date, taken}` | `MedLogOut` (UPSERTs by (med_id, date)) |

### AI Insights

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/insights/weekly` | — | `{week_start, text, stale}` (Claude Sonnet 4.5, ~180-260 words) |
| GET | `/api/insights/weekly` | — | `{week_start, text\|null, created_at?}` |
| POST | `/api/insights/email-digest` | — | `{ok:true, email_id}` — 400 if no insight cached or domain unverified |

### Correlations (Mood vs Diet)

| Method | Path | Query | Returns |
|---|---|---|---|
| GET | `/api/correlations` | `days?` (default 30, 1–180) | `{days, series: [{date, rating, protein_g, salt_g, water_ml}], correlations: {protein, salt, water, n}}` |

### Milestones & Community

| Method | Path | Returns |
|---|---|---|
| GET | `/api/milestones` | Personal records — 13 keys (see schemas below) |
| GET | `/api/community/averages` | Anonymous aggregates. Nulls returned when fewer than 5 users in window. |

### Dashboard (aggregate)

| Method | Path | Returns |
|---|---|---|
| GET | `/api/dashboard` | `{sobriety, today: {date, totals, diary, targets}, weekly_rating_avg, goals, week_start}` |

### Crisis Hotlines

| Method | Path | Returns |
|---|---|---|
| GET | `/api/crisis` | `{region, regions: [...], hotlines}` — hotlines is a dict {US, UK} if no region set, else a flat list |

### Reports & Email

| Method | Path | Query / Body | Returns |
|---|---|---|---|
| GET | `/api/reports/pdf` | `period=week\|month`, `scope=clinical\|full\|personal` | `application/pdf` attachment |
| POST | `/api/reports/email` | `{recipient_email, period, scope, note?}` | `{ok:true, email_id}` |

### Share Links (sponsor read-only)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/share-links` | `{expires_in_days (1-90), scope: "summary"\|"full"}` | `ShareLinkOut` |
| GET | `/api/share-links` | — | `[ShareLinkOut]` |
| DELETE | `/api/share-links/{id}` | — | `{ok:true}` (sets revoked=true) |

---

## Schemas

### `UserOut`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "sobriety_start": "YYYY-MM-DD" | null,
  "height_cm": number | null,
  "weight_kg": number | null,
  "region": "US" | "UK" | "" | null,
  "created_at": "ISO datetime"
}
```

### `DiaryIn` / `DiaryOut`
```json
{
  "date": "YYYY-MM-DD",
  "rating": 1-10,
  "mood_tags": ["Calm", "Hopeful", ...],
  "notes": "string"
}
// DiaryOut adds: id, created_at
```

### `MealIn` / `MealOut`
```json
{
  "date": "YYYY-MM-DD",
  "name": "string",
  "protein_g": number,
  "salt_g": number,
  "water_ml": number,
  "calories": number,
  "notes": "string"
}
// MealOut adds: id, created_at
```

### `BloodTestMarker`
```json
{ "name": "string", "value": number, "unit": "string", "reference_range": "string" }
```

### `BloodTestIn` / `BloodTestOut`
```json
{
  "date": "YYYY-MM-DD",
  "lab": "string",
  "markers": [BloodTestMarker],
  "notes": "string"
}
// BloodTestOut adds: id, created_at
```

### `GoalIn` / `GoalOut`
```json
{ "title": "string", "week_start": "YYYY-MM-DD (Monday)", "completed": bool }
// GoalOut adds: id, created_at
```

### `MedicationIn` / `MedicationOut`
```json
{
  "name": "string",
  "dose": "string",
  "schedule": "string",
  "notes": "string",
  "active": bool
}
// MedicationOut adds: id, created_at
```

### `MedLogIn` / `MedLogOut`
```json
{ "medication_id": "uuid", "date": "YYYY-MM-DD", "taken": bool }
// MedLogOut adds: id, created_at
```

### `ShareLinkOut`
```json
{
  "id": "uuid",
  "token": "url-safe 32 chars",
  "scope": "summary" | "full",
  "expires_at": "ISO datetime",
  "revoked": bool,
  "created_at": "ISO datetime"
}
```

### `MilestonesOut`
```json
{
  "current_streak_days": number,
  "best_protein_day": {"date": "YYYY-MM-DD", "protein_g": number} | null,
  "best_protein_streak": number,
  "days_meeting_protein": number,
  "days_within_salt": number,
  "diet_days_logged": number,
  "diary_entries": number,
  "avg_rating_all_time": number | null,
  "best_rating_day": {"date": "YYYY-MM-DD", "rating": number} | null,
  "best_7d_mood_avg": number | null,
  "best_7d_window_end": "YYYY-MM-DD" | null,
  "med_adherence_30d_pct": number | null,
  "goals_completed": number
}
```

---

## Targets & constants (mirror in mobile UI)

- Protein target: **≥ 140 g per day** (minimum)
- Salt limit: **≤ 2 g per day** (maximum)
- Water limit: **≤ 1.5 L (1500 ml) per day** (maximum — note: this is intentional per app brief, not a typo)
- Mood rating scale: **1–10** integer
- Sobriety streak: days since `sobriety_start` (UTC)
- Week start: **Monday** (ISO date)
- Community averages privacy threshold: **5 unique users** minimum

---

## Errors

All errors return:
```json
{ "detail": "string explanation" }
```

| Status | Meaning |
|---|---|
| 400 | Bad request — see `detail` (often Resend domain unverified, no insight cached, etc.) |
| 401 | Missing/invalid token |
| 404 | Resource not found OR cross-user access attempt |
| 410 | Share link revoked or expired |
| 422 | Validation error (bad enum, out-of-range value) |
| 502 | Upstream LLM or Resend failure |
| 503 | Service not configured (Resend not configured) |

---

## Image upload (food label, blood test extract)

- Accepted: **PNG, JPEG, WEBP only**
- Encoded as **base64 string** (no data URI prefix — just the base64 payload)
- Server-side max: ~10 MB before encoding recommended
- Response shape includes `raw_response` (the raw LLM text) — mobile clients can ignore this

---

## Mobile-specific recommendations

1. **Hit `GET /api/version` on cold start** — compare `min_mobile_client_version` against the bundled app version. If app is older, show an "Update available" banner.
2. **Cache JWT** in secure storage (Keychain on iOS, EncryptedSharedPreferences on Android).
3. **Reuse the existing backend** — do not stand up a new one. The web and mobile users share one database.
4. **All dates are ISO `YYYY-MM-DD`** (local date string, not datetime).
5. **All datetimes are ISO 8601 UTC** (with `+00:00` offset).
6. **For PDF report download on mobile**, use `GET /api/reports/pdf` and save via a native share sheet rather than triggering a browser download.

---

_Last updated: 2026-02. Contract version 1.0.0._
