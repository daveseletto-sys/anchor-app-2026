# Apple App Store — Resolution Center Reply (Copy & Paste)

**Use this when:** Apple has rejected your build under Guidelines **1.4.1 (Physical Harm)** and **5.1.1 (Privacy – Data Collection and Storage)** and the build currently with them already contains the Delete Account UI and the Medical Sources screen.

If the rejected build does **NOT** contain those fixes yet, first:
1. In Xcode, bump the **Build** number (e.g. 1 → 2).
2. Re-Archive → Distribute → Upload (or re-export the .ipa and upload via Transporter).
3. Wait until it appears in App Store Connect → **TestFlight** tab.
4. In App Store Connect → **App Store** tab → **Add Build** → pick the new build → **Submit for Review**.
5. Then paste the reply below into the Resolution Center.

---

## Reply 1 — short version (paste into Resolution Center)

Copy everything between the lines:

---
Hi App Review Team,

Thank you for the detailed feedback. We've addressed both guidelines in the build now attached to this submission. Specific in-app locations:

**Guideline 1.4.1 (Safety: Physical Harm) — Medical citations**
The app now displays the public-health source under every medical term. Reviewer can verify here:
1. Sign in with the test account below.
2. Open the **Glossary** tab → every term shows a tappable "Source:" link (NIAAA, MedlinePlus, NHS UK, Mayo Clinic, WHO, EFSA, NHMRC, etc.).
3. Open the **Diet Tracker** screen → the protein, salt, and water targets each cite their source (WHO 2g sodium guideline, NHMRC 1.5L fluid guideline, NHS 0.8 g/kg protein guideline).
4. Open **Profile → Medical references** (or visit the "Medical references" link from the Glossary footer) → the full list of 13 public-health sources is shown, with the medical disclaimer at the top: "Anchor is not a medical device and does not provide medical advice. The targets shown in this app are general adult guidance from public-health bodies, not personalised prescriptions. Speak to your doctor before changing diet, fluids, or medication, especially during alcohol withdrawal or recovery."
5. The disclaimer also appears on first launch as a one-time acknowledgement.

**Guideline 5.1.1 (Privacy: Data Collection and Storage) — In-app account deletion**
Users can now delete their account and all associated data from inside the app:
1. Sign in with the test account.
2. Tap **Profile** in the navigation.
3. Scroll to the bottom — **"Delete account"** section.
4. Tap **"Delete my account"** → type **DELETE** to confirm → tap **"Permanently delete"**.
5. The endpoint `DELETE /api/users/me` immediately and permanently removes the user along with every associated record (diary entries, meals, blood tests, medications, weekly goals, AI reflections, share links). No 30-day waiting period. Confirmed via the toast "Your account and all data have been deleted." and the user is returned to the sign-in screen.

**Test account (has seeded data so you can immediately see the deletion working):**
• Email: tester@anchor.app
• Password: Anchor!2026

After reviewing, please feel free to delete this test account yourself using the steps above — it is intended for review use.

**Privacy Policy:** https://progress-hub-256.emergent.host/privacy (clearly states what data is collected, how it is stored, that AI inference may use third-party processors with cropping recommended, and the self-service deletion path).

**Support / contact for further questions:** support@anchorhelp.com.au

Thank you for your time reviewing Anchor. We've worked hard to make sure this build addresses both guidelines completely.

Kind regards,
[Your Name]
Anchor Recovery
---

## Reply 2 — ultra-short version (if you prefer brevity)

Hi App Review Team,

Both guideline issues are addressed in the attached build:

• **5.1.1 — Account deletion:** Sign in (`tester@anchor.app` / `Anchor!2026`) → **Profile** → scroll to bottom → **Delete my account** → type **DELETE** → confirm. This calls `DELETE /api/users/me` and immediately removes the user and every associated record (diary, meals, blood tests, medications, goals, AI reflections, share links). No waiting period.

• **1.4.1 — Medical citations:** Every term in the **Glossary** shows a tappable "Source:" link to a public-health authority (NIAAA, MedlinePlus, NHS UK, Mayo Clinic, WHO, EFSA, NHMRC, etc.). Dietary targets in the **Diet Tracker** cite their sources. A full **Medical references** screen lists all 13 sources alongside the disclaimer "Anchor is not a medical device and does not provide medical advice. Targets shown are general adult guidance from public-health bodies, not personalised prescriptions. Speak to your doctor before changing diet, fluids, or medication." The disclaimer also appears as a first-launch acknowledgement.

Privacy Policy: https://progress-hub-256.emergent.host/privacy
Support: support@anchorhelp.com.au

Thanks for the careful review.

---

## How to send the reply in App Store Connect

1. Open the rejection email (or App Store Connect → **Apps** → Anchor → **App Review** → the rejected submission).
2. Click **View Submission** → scroll to the **Resolution Center** at the bottom (it looks like a chat thread with Apple).
3. Paste the reply into the message box (Reply 1 is recommended — Apple reviewers like specific in-app paths).
4. Click **Send**.
5. If you uploaded a **new build** to fix this, go to **App Store** tab → **Add Build** → pick the new build → **Save** → **Add for Review** → **Submit for Review** (the reply alone won't re-trigger review unless attached to a new build OR you explicitly request a re-review).

Average re-review turnaround after a reply + new build: **24–48 hours**.

---

## If Apple still rejects after this

The most common reason a recovery / health app keeps getting 1.4.1 flags is missing inline citations on **specific screens**, not just in the Glossary. Make sure the iOS app also shows the disclaimer **on the very first launch** (one-time modal) and on screens that show numeric medical targets (Diet Tracker, Blood Tests). If it still gets rejected, request a phone call with App Review from the Resolution Center — they are usually willing to walk you through exactly what they want to see.
