# Anchor Recovery — iOS app (Expo)

This is the iOS app for Anchor Recovery. It wraps the production web app
(`https://progress-hub-256.emergent.host`) inside a native iOS shell with:

- ✅ Native splash screen and warm sand background
- ✅ **One-tap region-aware crisis call button** (988 US / Samaritans UK / Lifeline AU) — pure native, uses `tel:` URL scheme
- ✅ Native offline detection + retry screen
- ✅ Native pull-to-refresh and back-gesture support
- ✅ Native haptic feedback on key actions
- ✅ Native file/camera picker (handles iPhone HEIC photos automatically)
- ✅ Inherits all web-app features: diary, diet tracking, food label scanner, blood test OCR, medications, weekly goals, AI weekly reflection, clinician PDF export, sponsor share links, account deletion, medical sources/citations.

> The Apple Guideline 4.2 "minimum functionality" bar is satisfied by the native crisis-line button, native offline/retry, native splash, native haptics, native file picker, and native deep-link handling. This is *not* a pure WebView — it's a thin native shell around a fully-functional medical companion.

---

## What you need on your Mac (one-time setup, ~15 min)

1. **Apple Developer account** (you already have this — $99/yr)
2. **Node.js 20 LTS or newer** — open Terminal and run:
   ```bash
   node --version
   ```
   - If you see `v20.x.x` or higher → ✅ skip ahead
   - If you see "command not found" or older version → download from https://nodejs.org (pick the "LTS" version, run the installer)
3. **An Expo account** — go to https://expo.dev and sign up (free). Save the email/password somewhere.

---

## Build & submit — copy-paste, top to bottom

Open **Terminal** on your Mac (Cmd+Space → type "Terminal" → Enter) and run these commands one by one:

### 1. Clone this repository

```bash
cd ~/Desktop
git clone https://github.com/daveseletto-sys/anchor-app-2026.git
cd anchor-app-2026/mobile
```

(If your repo is named differently, replace `anchor-app-2026` with the right name.)

### 2. Install dependencies

```bash
npm install
```

(Takes 1–3 minutes. You'll see lots of text — wait for the prompt to come back.)

### 3. Install the EAS command-line tool (Expo's cloud builder)

```bash
npm install -g eas-cli
```

### 4. Log into your Expo account

```bash
eas login
```

(Type your expo.dev email, hit Enter, type your password, hit Enter.)

### 5. Link this project to your Expo account

```bash
eas init
```

(It will ask you to confirm — say **yes**. It auto-generates a project ID.)

### 6. Fill in your Apple details (one tiny edit)

Open `eas.json` in any text editor (TextEdit is fine) and replace the three `REPLACE_WITH_…` placeholders:

- `appleId` → the email you log into App Store Connect with (e.g. `you@example.com`)
- `ascAppId` → the numeric App ID from App Store Connect. Find it: App Store Connect → My Apps → Anchor → App Information → "Apple ID" field (it's a 10-digit number, NOT your email).
- `appleTeamId` → 10-character team ID. Find it: https://developer.apple.com/account → Membership → "Team ID".

Save the file.

### 7. Build the iOS app in the cloud

```bash
eas build --platform ios --profile production
```

EAS will ask:
- "What would you like your iOS bundle identifier to be?" → press **Enter** (it'll use `au.com.anchorhelp.anchor` from the config)
- "Do you want to log in to your Apple account?" → **Y**
- It will prompt for your Apple ID password and two-factor code → enter them
- "Generate a new Apple Distribution Certificate?" → **Y**
- "Generate a new Apple Provisioning Profile?" → **Y**
- EAS then runs the build in their cloud (no Xcode needed!) — this takes **15–25 minutes**
- You'll get a link like `https://expo.dev/accounts/.../builds/abc123` — open it in your browser to watch progress

When it's done, you'll see ✅ Build finished. The `.ipa` is downloaded by Apple automatically — you don't need to touch it.

### 8. Submit the build to App Store Connect

```bash
eas submit --platform ios --latest
```

- It uses your latest finished build automatically
- Confirms via your Apple ID
- Uploads to App Store Connect (~5 minutes)

When done, the build appears in App Store Connect → **TestFlight** tab within ~15 minutes. From there:

1. Go to App Store Connect → **Apps** → **Anchor Recovery** → **App Store** tab
2. Make sure the version is "1.0 Prepare for Submission" (or create new version if needed)
3. Scroll to **Build** section → **+ Add Build** → pick your new build (Build 2)
4. Save → **Add for Review** → **Submit for Review**
5. In the **Resolution Center** of the rejected submission, paste the reply from `APPLE_RESOLUTION_REPLY.md` in this repo.

---

## Re-build later (after the first time)

Just bump the build number in `app.json` (`"buildNumber": "2"` → `"3"`) and run:
```bash
eas build --platform ios --profile production
eas submit --platform ios --latest
```

(EAS's `autoIncrement: true` in `eas.json` does this for you on production builds, but it doesn't hurt to set it manually.)

---

## Test it on your phone WITHOUT going through App Store first (recommended!)

After step 7 succeeds:
1. Open https://expo.dev → your account → Builds → the latest finished build
2. Click the build → "Install" → scan the QR code with your iPhone camera
3. Install the profile (Settings → General → VPN & Device Management → trust the profile)
4. Open the app — it should load Anchor Recovery and you can test:
   - Sign in (`tester@anchor.app` / `Anchor!2026`)
   - Profile → scroll down → **Delete account** (works!)
   - Glossary → tap "Source:" on any term (opens citation)
   - Food Label → take a photo with iPhone camera → AI extracts (the HEIC fix means this now works!)
   - Blood Tests → upload lab report photo → AI extracts markers
   - Tap **"Need help now?"** button bottom-right → see crisis numbers → tap one → confirms native call dialog

If everything works, submit to App Store.

---

## Common pitfalls and how to fix them

- **`eas: command not found` after step 3** → run `export PATH="$PATH:$(npm bin -g)"` then retry.
- **Apple two-factor code never arrives** → it goes to one of your *Apple devices* (iPhone/Mac), not SMS. Check your iPhone notification center.
- **"Bundle identifier is already registered to another team"** → in App Store Connect → Certificates, Identifiers & Profiles → Identifiers → search `au.com.anchorhelp.anchor` → confirm it's owned by your team. If not, register it.
- **Apple still rejects** → the most common follow-up is "we need a screen recording showing account deletion". Open the app on your iPhone (via TestFlight) → record screen (swipe down from top right → record button) → log in → Profile → scroll → Delete → DELETE → confirm → screen recording done. Upload the .mov file in the Resolution Center reply.

---

## Files in this project

```
mobile/
├── App.js          ← the entire native shell (~250 lines, has the crisis button, offline state, etc.)
├── index.js        ← Expo entry point
├── app.json        ← Expo config (bundle ID, permissions, splash, icon)
├── eas.json        ← EAS build/submit config — EDIT before first submit (step 6)
├── babel.config.js
├── package.json
└── assets/
    ├── icon.png            ← 1024x1024 app icon (placeholder — replace with real Anchor logo before launch)
    ├── splash.png          ← Splash screen
    ├── adaptive-icon.png   ← Android adaptive icon
    └── favicon.png         ← Web favicon (unused for iOS)
```

The web app it points at is configured in `app.json` under `extra.appUrl`. If you ever redeploy the web app to a new URL, change that and rebuild.
