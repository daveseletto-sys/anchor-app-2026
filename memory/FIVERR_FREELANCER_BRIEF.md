# Anchor Recovery — iOS App Build Brief (for Fiverr Freelancer)

**Hi! 👋** This document has everything you need to build and submit the iOS app for **Anchor Recovery** to the Apple App Store.

The web version is already live, the backend is production-ready, and the App Store has previously rejected the app on two specific guidelines that this brief addresses head-on.

---

## What you're building

A native iOS app that talks to an already-deployed backend. **You don't need to build a backend.** The backend is live, tested, documented, and shared between the web app and the iOS app. You just need to build the iOS client that calls it.

- **App name:** Anchor — Recovery (or "Anchor Recovery")
- **Bundle ID / SKU:** `au.com.anchorhelp.anchor`
- **Category:** Health & Fitness (primary), Medical (secondary)
- **Age rating:** 17+ (alcohol references)
- **Target audience:** Adults managing alcohol use disorder
- **Tone:** Warm, supportive, non-clinical, never judgmental, never gamified against other users

## Backend (already deployed — DO NOT rebuild)

- **Production base URL:** `https://progress-hub-256.emergent.host/api`
- **Auth:** JWT (HS256) email + password, header `Authorization: Bearer <token>`
- **Test account:**
  - email: `tester@anchor.app`
  - password: `Anchor!2026`
  - (has ~6 weeks of seeded data — useful for screenshots and Apple reviewer)

## Critical — fixes required for Apple App Store

Apple previously rejected this app for these two guideline violations. Both fixes MUST be in the iOS app you submit:

### 1. Guideline 5.1.1(v) — Account deletion (MANDATORY)

The iOS app must let the user **delete their own account from inside the app**. Implementation:

- Add a "Delete account" section to the Profile / Settings screen (call it "Danger zone")
- Tapping it shows a confirmation modal requiring the user to **type DELETE** to enable a destructive confirm button
- On confirm, call: `DELETE /api/users/me` with Bearer token
- On success: clear the token from Keychain → navigate to login screen → show toast "Your account and all data have been deleted."
- Response from the API: `{ok: true, deleted: true}` — handle errors (display the `detail` from the response)

### 2. Guideline 1.4.1 — Medical citations (MANDATORY)

The iOS app must show citations for medical information. Implementation:

- The Glossary endpoint `GET /api/glossary` now returns each term with `source_name` and `source_url` — display them as a tappable "Source: ..." link beneath each definition (open in `SFSafariViewController`)
- Add a new "Medical references" screen that calls `GET /api/sources` and displays the returned `sources` list (name + url + purpose) plus the `disclaimer` text at the top in a highlighted card
- Link to the Medical references screen from:
  - The Glossary screen footer
  - The Diet Tracker screen header (citing the dietary targets)
  - The About/Profile screen
- Show the disclaimer text from `GET /api/sources` on first launch (one-time onboarding dialog) and in the About screen

## App Store Connect — text to paste

### Privacy Policy URL
`https://progress-hub-256.emergent.host/privacy`

### Support URL
`https://progress-hub-256.emergent.host/support`

### Marketing URL (optional)
`https://anchorhelp.com.au` _(or leave blank)_

### App Name
**Anchor — Recovery**

### Subtitle (30 char max)
**A private recovery companion**

### Short description / promotional text (170 char max)
> Track your recovery your way. Diary, diet, blood test trends, food label scanner, weekly goals. Private, supportive, never judgmental. One steady day at a time.

### Long description
A private companion for people in alcohol recovery. Track sobriety, mood, diet, blood markers, medications, and weekly goals. AI-powered weekly reflections. Clinician-ready PDF reports. Anonymous community averages. Never gamified.

(Full long description available at request — see `/app/memory/APP_STORE_METADATA.md` in the source.)

### Keywords (100 char max, comma-separated)
**alcohol,recovery,sobriety,sober,addiction,liver,health,tracker,diary,wellness**

### App Review Notes — PASTE THIS EXACT TEXT
```
Test account:
  email: tester@anchor.app
  password: Anchor!2026

This account has ~6 weeks of seeded data including diary entries, meal logs,
blood test results, medications, weekly goals, and an AI weekly reflection.

Account deletion (Guideline 5.1.1(v)) is available in-app at:
  Profile → Delete account → type DELETE → confirm
The endpoint immediately and permanently removes the user and ALL associated data.

Medical citations (Guideline 1.4.1) are shown inline in:
  • Glossary (every term shows its source — NIAAA, MedlinePlus, NHS UK, Mayo Clinic, etc.)
  • Diet Tracker (citing WHO, NHMRC, EFSA for dietary targets)
  • Medical References screen (full list of public health sources used in the app)
A medical disclaimer is shown on first launch and in the About screen.

AI features (food label reader, blood test extractor, weekly reflection) use OpenAI
and Anthropic models via the Emergent Integrations gateway. Users are warned in the
Privacy Policy and Support FAQ to crop or hide identifying information before
uploading lab reports.

Contact for any review questions: support@anchorhelp.com.au
```

## All API endpoints the iOS app should call

| Method | Path | Purpose |
|---|---|---|
| GET | /api/version | Cold-start compatibility check (handles 404 gracefully) |
| POST | /api/auth/register | Sign up |
| POST | /api/auth/login | Sign in |
| GET | /api/auth/me | Current user |
| POST | /api/auth/change-password | Password change |
| **DELETE** | **/api/users/me** | **Account deletion (REQUIRED for Apple)** |
| PATCH | /api/users/me | Update profile (name, sobriety_start, height_cm, weight_kg, region) |
| GET | /api/dashboard | Aggregate dashboard data |
| GET | /api/sobriety, PATCH /api/sobriety | Sobriety streak |
| GET/POST/DELETE | /api/diary | Daily mood entries |
| GET/POST/DELETE | /api/meals | Meal log |
| GET | /api/meals/totals | Today's totals |
| POST | /api/water | Quick water log |
| GET/POST/DELETE | /api/blood-tests | Blood test results |
| POST | /api/blood-tests/extract | AI extraction from photo |
| POST | /api/food-label/analyze | AI nutrition from label photo |
| GET/POST/PATCH/DELETE | /api/goals | Weekly goals |
| GET/POST/PATCH/DELETE | /api/medications | Medications |
| GET/POST | /api/medications/log | Daily med check-offs (upsert) |
| POST/GET | /api/insights/weekly | AI weekly reflection (Claude) |
| POST | /api/insights/email-digest | Email reflection to user |
| GET | /api/correlations | Mood-vs-diet correlation data |
| GET | /api/milestones | Personal records (NOT a leaderboard) |
| GET | /api/community/averages | Anonymous community averages (≥5 user threshold) |
| GET | /api/crisis | Region-aware crisis hotlines |
| GET | /api/reports/pdf | Download PDF report |
| POST | /api/reports/email | Email PDF to doctor |
| POST/GET/DELETE | /api/share-links | Sponsor share links |
| GET | /api/shared/{token} | PUBLIC — sponsor view (no auth) |
| **GET** | **/api/glossary** | **Now includes source_name + source_url per term (REQUIRED for Apple)** |
| **GET** | **/api/sources** | **Medical references list (REQUIRED for Apple)** |

## Design

- **Aesthetic:** Warm, earthy — bone/sand backgrounds, sage primary, terracotta accent. NOT clinical blue, NOT purple gradients.
- **Fonts:** Outfit (display headings) + Work Sans (body)
- **See the web app to match the look:** `https://progress-hub-256.emergent.host` (test login above)

## Critical UX rules (this app is for vulnerable users)

1. **Sobriety counter** is the dashboard hero — large, sage, NEVER red even on day 0
2. **Salt and water** cards turn terracotta when over limit (these are MAX limits)
3. **Protein** fills sage at 140g target (this IS a goal)
4. **No leaderboards, no comparison, no streaks pressure** against other users
5. **Crisis link** ("Need help now?") must be accessible from any screen — recommend tab bar item
6. **Mood tags chips:** Calm, Hopeful, Tired, Anxious, Craving, Strong, Lonely, Grateful, Restless, Focused
7. Week starts **Monday** (ISO date)

## Native-specific must-haves

- **JWT stored in Keychain** (not UserDefaults)
- **Native share sheet** for PDF reports + share links
- **Pull-to-refresh** on Dashboard, Diary, Diet, Milestones, Blood Tests
- **Haptic feedback** on goal completion, streak milestones, account deletion confirm
- **expo-image-picker** for camera capture in Food Label / Blood Test (PNG/JPEG/WEBP, base64 encode)
- **Loading state of 5–25 seconds** on AI calls (food label, blood test extract, weekly insight)
- **Cold-start version check** against `/api/version` (handle 404 gracefully)

## Deliverables I'm expecting

1. iOS app `.ipa` uploaded to App Store Connect via Transporter (or built directly through Xcode → Archive → Upload)
2. Bundle ID configured as `au.com.anchorhelp.anchor`
3. App icon designed (1024×1024 + all required sizes — use the Anchor symbol on a warm sand background)
4. Six screenshots for 6.7" iPhone (1290×2796) from iOS Simulator
5. Three screenshots for 12.9" iPad (2048×2732) if you support iPad
6. Submission to Apple with the exact review notes from earlier in this doc
7. Send me the App Store Connect "TestFlight" link so I can test before going live

## What success looks like

- The iOS app builds and runs against the live backend (no separate backend needed)
- Apple App Store review **passes** (no 5.1.1(v) or 1.4.1 rejections)
- App appears in the App Store under "Health & Fitness" with the 17+ rating
- Submission turnaround: typically 24–72 hours for Apple review

---

## Quick handover checklist for me (the buyer)

When you're done, I should be able to:
- [ ] Install the app from TestFlight on my iPhone
- [ ] Log in with `tester@anchor.app` / `Anchor!2026`
- [ ] See my web data appear in the iOS app (same backend)
- [ ] Open the Glossary and see "Source:" links under each term
- [ ] Open the Medical References screen and see the disclaimer + 13 sources
- [ ] Open Profile → Delete account → type DELETE → confirm → see my account vanish
- [ ] Confirm a new account creates fresh on register, syncs to web

---

## Contact

- App owner: _[your name and email]_
- Web app: https://progress-hub-256.emergent.host
- Support email: support@anchorhelp.com.au
- Backend documentation: ask for the API contract — has every endpoint's request/response schema

Thanks for taking this on. The hard part (backend, design, recovery-research-informed UX, App Store metadata) is done — you're getting a clean, well-defined client-build job. 🤝
