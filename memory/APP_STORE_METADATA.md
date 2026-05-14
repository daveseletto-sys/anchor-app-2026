# Anchor — App Store Metadata

## App Name (30 char max)
**Anchor — Recovery** _(18 chars)_

Alternates:
- Anchor: Sober Companion _(23)_
- Anchor _(6)_ — cleanest if available; "Anchor" alone may be taken on the App Store, check first

## Subtitle (30 char max)
**A private recovery companion** _(28 chars)_

Alternates:
- One steady day at a time _(24)_
- Track. Reflect. Heal. _(22)_

## Promotional Text (170 char max — editable post-launch without re-review)
Use this slot for time-limited messages or recent updates. Suggested launch copy:

> New: AI weekly reflections + clinician PDF reports. Track your mood, diet, blood markers, and goals — all in one quiet, judgment-free place.

## Short Description / Search line (170 char max)
**Track your recovery your way. Diary, diet, blood test trends, food label scanner, weekly goals. Private, supportive, never judgmental. One steady day at a time.** _(152 chars)_

## Long Description (4000 char max) — DRAFT
> Anchor is a private companion for people in alcohol recovery. It quietly tracks the small things that rebuild a life — mood, meals, hydration, blood markers, medications, and weekly goals — and turns them into a clear picture of healing over time.
>
> WHAT YOU CAN DO
> • Daily diary — rate your day 1–10 and tag your mood. No judgment, just a record.
> • Diet tracker — log meals against recovery-friendly targets (protein, salt, water).
> • AI food label reader — snap a nutrition label and Anchor extracts the values for you.
> • Blood test trends — log liver markers (ALT, AST, GGT, bilirubin, MCV) or upload a report image and let AI extract them. Watch them heal across time.
> • Weekly goals — small, doable commitments. One week at a time.
> • Medications — track Naltrexone, thiamine, supplements, and tick them off daily.
> • Sobriety streak — a quiet, steady counter for the days you've shown up for yourself.
> • Weekly AI reflection — a warm, private 200-word summary of your week.
> • Crisis hotlines — US and UK helplines, one tap away.
> • Clinician-ready PDF reports — share with your doctor, therapist, or sponsor.
> • Sponsor share links — read-only, expiring links you control.
> • Glossary — recovery and medical terms in plain language.
>
> PRIVATE BY DESIGN
> Your data is yours. You decide what to share, with whom, and for how long. Anchor never ranks you against other users.
>
> NOT A SUBSTITUTE FOR CLINICAL CARE
> Anchor is a self-tracking tool. It supports your recovery — it does not replace medical advice, therapy, or emergency care. If you are in crisis, the in-app helplines connect you to people who can help.

## Keywords (100 char total, comma-separated, no spaces after commas)
**alcohol,recovery,sobriety,sober,addiction,liver,health,tracker,diary,wellness**
_(73 chars — leaves room to A/B test additions like "AA","SMART","detox")_

## Category
**Primary:** Health & Fitness
**Secondary:** Medical

## Age Rating
**17+** — required for any app with content related to alcohol use, even when the app is *helping* someone stop drinking. Reason: Apple's "Frequent/Intense References to Alcohol, Tobacco, or Drug Use."

## SKU
**`au.com.anchorhelp.anchor`** — locked in (matches Bundle ID, unchangeable after first save in App Store Connect)

## URLs you'll need
- **Privacy Policy URL** — Required. → `https://anchorhelp.com.au/privacy` (after deploy of web app to that domain, OR `https://progress-hub-256.emergent.host/privacy`)
- **Support URL** — Required. → `https://anchorhelp.com.au/support` (or `https://progress-hub-256.emergent.host/support`)
- **Marketing URL** — Optional. → `https://anchorhelp.com.au`

## In-App Purchases / Pricing
- Suggested: **Free**, no IAP for launch
- If you later add a Pro tier, the App Store requires you to use Apple's IAP (Apple takes 15–30%). Subscription products would need to be re-reviewed.

## Screenshots needed (6.7" iPhone — required, 1290×2796px)
At least **3 screenshots**. Suggested 6:
1. Dashboard — streak + diet rings + today's mood
2. Daily diary — mood slider + tags
3. Food label scanner — camera + AI result
4. Blood test trends — chart of ALT/AST over time
5. Weekly AI reflection card
6. Milestones — personal records

iPad screenshots optional but recommended if app supports iPad.

## App Review Notes (for Apple reviewer)
> Anchor is a self-tracking tool for adults managing alcohol use. It does not promote alcohol consumption — it supports abstinence. AI features use OpenAI and Anthropic models via the emergentintegrations gateway, with no PII sent in image extraction (food labels and blood reports only). Test credentials: tester@anchor.app / Anchor!2026

---

_Last updated: 2026-02. Paste these fields into App Store Connect when ready._
