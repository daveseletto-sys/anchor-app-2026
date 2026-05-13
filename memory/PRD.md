# Anchor — Recovery Companion (PRD)

## Original Problem Statement
"build me an app for alcoholics to monitor there progress diet, blood test results, food label reader, weekly goals, daily diary on progress with a daily rating on how they have done for the day min protein intake 140mg daily no more than 2mg salt no more than 1.5 litres of water a day. glossary of terms inc"

> Note: units interpreted as grams (industry standard): protein ≥ 140 g/day, salt ≤ 2 g/day, water ≤ 1.5 L/day.

## User Choices
- Auth: Email + Password (JWT)
- Food label reader: AI-powered (GPT-5.2 vision)
- Daily rating: 1–10 slider + mood tags
- Blood tests: manual entry + AI extraction (both)
- Design: Warm/supportive, earthy tones

## Architecture
- **Backend**: FastAPI + MongoDB (motor). JWT auth (HS256, bcrypt). LLM via `emergentintegrations` (`gpt-5.2` for image analysis).
- **Frontend**: React 19, Tailwind, Shadcn UI, Recharts, Sonner toasts, Lucide icons. Fonts: Outfit + Work Sans.

## User Personas
1. **Person in early recovery** — needs gentle, non-judgmental tracking; wants to see liver markers heal.
2. **Person managing long-term sobriety** — wants streak counter, nutrition discipline, weekly accountability.

## Core Requirements (static)
- Sobriety streak counter (days since start)
- Daily diary (1–10 rating + mood tags + notes)
- Diet tracker (protein ≥ 140 g, salt ≤ 2 g, water ≤ 1.5 L)
- Food label reader (AI nutrition extraction)
- Blood test results (manual + AI extraction; trends/charts)
- Weekly goals (week-based, checkable)
- Glossary (recovery/medical terms)

## Implemented (2026-02 / Iteration 1)
- ✅ JWT auth: register, login, /me
- ✅ Sobriety: GET / PATCH
- ✅ Diary CRUD with rating + mood tags
- ✅ Meals CRUD + totals + quick water
- ✅ Blood tests CRUD + AI extraction (`gpt-5.2` vision)
- ✅ Food label AI analysis (`gpt-5.2` vision)
- ✅ Weekly goals CRUD with completed toggle
- ✅ Glossary (31 curated terms)
- ✅ Dashboard aggregate endpoint
- ✅ Warm/earthy UI: bento dashboard, progress rings, tactile cards, asymmetric auth landing
- ✅ Recharts trends for blood markers
- ✅ 19/19 backend pytest tests passing

## Implemented (2026-02 / Iteration 2 — P1)
- ✅ Editable profile: name, sobriety_start, height_cm, weight_kg + change-password
- ✅ Medication tracker: CRUD + daily check-offs with upsert + cascade delete on logs
- ✅ AI Weekly Insights via Claude Sonnet 4.5
- ✅ 30/30 backend tests passing

## Implemented (2026-02 / Iteration 3 — P2)
- ✅ Crisis hotlines + region-aware UI
- ✅ Clinician PDF reports (period × scope)
- ✅ 43/43 backend tests passing

## Implemented (2026-02 / Iteration 4 — P3)
- ✅ Mood-vs-diet correlation chart on Dashboard (Recharts ComposedChart, 30-day Pearson correlations)
- ✅ Sponsor read-only share links with expiring tokens (revocable, scope summary/full)
- ✅ Public `/share/{token}` route — no login required for viewer
- ✅ 63/63 backend tests passing
- ✅ Moved `import secrets` to top of server.py

## Prioritized Backlog
**P4 (next)**
- Email reminders (Resend) — needs API key
- "Email this report to my doctor" one-click flow
- AI insights weekly email digest

**P5 (later)**
- Sora-2 / image-based shareable weekly recap
- Mobile PWA install + push notifications
- Split server.py into routers (auth, diary, share, etc.) for maintainability

## Next Action Items
- Get user feedback on first build
- Consider weekly AI insight summary as next feature (high value, leverages existing diary + diet data)
