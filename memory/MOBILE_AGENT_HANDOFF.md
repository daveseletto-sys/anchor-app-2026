# Mobile Agent — Handoff Brief

> **Copy and paste this entire file** into the Mobile Agent as the first message of your new Expo / React Native project. It contains everything needed to rebuild Anchor Recovery for iOS while reusing the existing production backend.

---

## Project

**App name:** Anchor — Recovery Companion
**Type:** Native iOS app (Expo / React Native), to be published to Apple App Store
**Bundle ID / SKU:** `au.com.anchorhelp.anchor`
**Target audience:** Adults (17+) managing alcohol use disorder
**Tone:** Warm, supportive, non-clinical, never judgmental

## Reuse the existing backend — do NOT build a new one

The web version is already live at `https://progress-hub-256.emergent.host` with a fully-tested FastAPI backend. All endpoints are under `/api`. The mobile app must talk to this backend so mobile and web users share one database.

- **Production base URL:** `https://progress-hub-256.emergent.host/api`
- **Auth:** JWT (HS256) email + password — `Authorization: Bearer <token>` on every authenticated request
- **API contract:** see `/app/memory/API_CONTRACT.md` in the source for every endpoint, schema, and error code

## Features to replicate (priority order)

1. **Auth** — register / login / change password (POST /api/auth/register, /api/auth/login, /api/auth/change-password)
2. **Dashboard** — sobriety streak hero, today's diet rings (protein/salt/water), today's mood, weekly insight card (GET /api/dashboard)
3. **Daily diary** — 1–10 mood slider + mood-tag chips + free-text notes (GET/POST/DELETE /api/diary)
4. **Diet tracker** — log meals manually, daily totals, quick-water buttons (GET/POST/DELETE /api/meals, GET /api/meals/totals, POST /api/water)
5. **Food label reader** — camera capture → base64 → POST /api/food-label/analyze → confirm fields → add as meal
6. **Blood tests** — manual entry of markers OR camera upload to POST /api/blood-tests/extract; trends chart for ALT/AST/GGT/etc.
7. **Medications** — list, add, daily check-off toggle (cascades to /api/medications/log upsert)
8. **Weekly goals** — list/add/toggle for current Monday-week
9. **Reports** — period × scope picker → download PDF (GET /api/reports/pdf) → native share sheet
10. **Share links** — generate sponsor links → copy or native share
11. **Milestones** — personal records page + anonymous community averages
12. **Profile** — name, sobriety_start, height, weight, region (US/UK/Both)
13. **Crisis hotlines** — region-aware list, with persistent "Need help now?" tab bar item
14. **Glossary** — searchable list of recovery/medical terms
15. **Weekly AI insight** — POST /api/insights/weekly to generate, GET to read cached. Optional "Email me" via POST /api/insights/email-digest

## Design

- **Aesthetic:** Warm, earthy — bone/sand backgrounds, sage primary, terracotta accent
- **Fonts:** Outfit (display) + Work Sans (body) — both on Google Fonts; use `expo-google-fonts`
- **Avoid:** purple gradients, generic medical-blue, harsh black/white contrast
- See production web app for the look: `https://progress-hub-256.emergent.host`

## Critical UX rules

- **Sobriety counter** is the hero on Dashboard — large, sage colour, never red even on day 0
- **Salt and water** charts/cards turn terracotta (warm warning, not red) when over limit — these are LIMITS, not goals
- **Protein** chart fills sage when meeting 140g target — this IS a goal
- **No leaderboards / no competition / no streaks pressure** — recovery is private, never gamified against other users
- **Mood tags** are chips: Calm, Hopeful, Tired, Anxious, Craving, Strong, Lonely, Grateful, Restless, Focused
- **Targets** are: protein ≥ 140 g/day, salt ≤ 2 g/day, water ≤ 1500 ml/day (yes, water is a max — this is intentional per the recovery dietary brief)
- **Week starts Monday** (ISO date string)
- **Crisis link** must be accessible from any screen — recommend tab bar or persistent header button

## Image upload (food label / blood test)

- Use `expo-image-picker` with camera + gallery
- Allowed types: PNG, JPEG, WEBP only
- Convert to base64 (no data URI prefix) before POSTing
- Show a loading state — LLM calls take 5–25 seconds
- Allow user to edit extracted values before saving

## Native-specific touches expected

- **Secure JWT storage** — use `expo-secure-store` (Keychain on iOS)
- **Pull-to-refresh** on Dashboard, Diary, Diet, Milestones
- **Native share sheet** for PDF reports and share links
- **Push notifications** (optional, P2): daily check-in reminder at user-chosen time
- **Cold-start version check** — call GET /api/version, compare `min_mobile_client_version` to bundled version, show update banner if behind
- **Haptic feedback** on goal completion / streak milestones

## Test account

- Email: `tester@anchor.app`
- Password: `Anchor!2026`
- This account has ~6 weeks of data — useful for screenshots and demo

## App Store metadata (already prepared)

See `/app/memory/APP_STORE_METADATA.md` for: app name, subtitle, short description, long description (4000 chars), keywords, age rating reasoning (17+), category, support URL (`https://progress-hub-256.emergent.host/support`), privacy URL (`https://progress-hub-256.emergent.host/privacy`).

## Things to defer (P2)

- In-app purchases / subscriptions — launch free
- Apple Health / HealthKit integration — would be a great addition later
- Apple Watch companion — same
- Dark mode — match system

---

_Generated 2026-02. Web app version: 1.0.0._
