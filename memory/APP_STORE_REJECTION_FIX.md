# Apple App Store Rejection — Resolution Notes

## Original rejection (received 2026-02)

Apple rejected the Anchor Recovery iOS app with **two guideline violations**:

### 1. Guideline 5.1.1(v) — Data Collection and Storage
> App supports account creation but does not include a mechanism to **initiate account deletion** from within the app. Apps that allow signup must offer self-service account deletion.

### 2. Guideline 1.4.1 — Safety: Physical Harm
> The app includes medical information without **citations from credible sources**.

---

## Fixes — what's now in the web app & backend

### Account deletion (5.1.1 v)
- **Endpoint:** `DELETE /api/users/me`
  - Authenticated. Cascade-deletes user + ALL data (diary, meals, blood_tests, medications, med_logs, goals, weekly_insights, share_links)
  - Returns `{ok:true, deleted:true}`. Token becomes invalid; subsequent requests get 404/401.
- **Frontend:** Profile page → **Danger zone** card → "Delete my account" button → user must type `DELETE` to enable confirm button → calls endpoint → logs out → redirects to landing
- **Privacy Policy and Support FAQ updated** to clearly describe self-service deletion

### Medical citations (1.4.1)
- **Glossary** (`/app/glossary`): every one of the 31 terms now displays its citation inline — e.g. _"Source: MedlinePlus (NIH)"_ with a link to the original page
- **New `/sources` public page**: lists 13 primary references (NIAAA, MedlinePlus, SAMHSA, NHS UK, Mayo Clinic, WHO, NHMRC, EFSA, AA, SMART Recovery, Samaritans, 988 Lifeline, Lifeline AU) with what each is used for, plus a medical disclaimer
- **`GET /api/sources`** public endpoint returns `{sources, disclaimer}` for any client to use
- **Diet Tracker** page header now cites WHO/NHMRC/EFSA for the default targets, with a link to `/sources`
- **Glossary footer** links to `/sources` and shows the medical disclaimer

---

## What the Mobile Agent needs to add to the iOS app

Paste this into the Mobile Agent so the iOS submission passes review:

```
Two App Store review fixes needed before resubmission:

1. ACCOUNT DELETION (Guideline 5.1.1 v) — add a "Delete account" flow:
   • Settings/Profile screen → bottom "Danger zone" card
   • Tap "Delete my account" → modal asks user to type DELETE to confirm
   • Confirm → DELETE /api/users/me (Bearer token in header)
   • On success → clear Keychain token → navigate to landing/login
   • Show toast/alert: "Your account and all data have been deleted."

2. MEDICAL CITATIONS (Guideline 1.4.1) — display sources for medical info:
   • In the Glossary screen, each term has fields source_name and source_url
     coming from GET /api/glossary — render these as a tappable "Source: X" 
     link beneath each definition that opens the URL in Safari View Controller.
   • Add a "Medical references" screen (route /sources or similar) that calls 
     GET /api/sources and lists sources[].name with sources[].url and 
     sources[].purpose, plus a disclaimer box at the top with the returned 
     disclaimer string.
   • Add a link to the Sources screen from: Glossary footer, Diet Tracker 
     header (citing the dietary targets), and Profile/About screen.
   • Include the medical disclaimer text on first launch or in About screen.

Backend endpoints are already live:
- DELETE /api/users/me
- GET /api/sources
- GET /api/glossary (now returns source_name + source_url on each item)

App Store review notes — add this exact text in App Store Connect:
"Account deletion is available in-app at Profile > Delete account. Medical 
information is cited inline in the Glossary, in the Diet Tracker, and on the 
dedicated Medical References screen. All citations link to public health 
sources including NIAAA, MedlinePlus, NHS UK, Mayo Clinic, WHO, SAMHSA, and 
NHMRC."
```

---

## After Mobile Agent finishes

1. Submit the new iOS build via TestFlight / App Store Connect
2. In the App Store Connect submission form, paste the review note from the section above into "Notes for the App Review team"
3. Test the account deletion flow once on a real device before submission — Apple reviewers will test this themselves
4. Common follow-up requests from Apple:
   - "Please show us in a screen recording" — record a 30-second clip of Settings → Delete account → confirm → success
   - Privacy URL should be reachable without login (ours is — confirmed)

---

_Generated 2026-02 in response to App Store rejection screenshot._
