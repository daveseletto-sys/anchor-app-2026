# IMPORTANT — Before EVERY iOS rebuild

EAS Build runs on Apple's latest Xcode (currently Xcode 26+). The pinned
package versions in `package.json` are a baseline; the **actual** versions
required for a given Xcode release change as Apple updates the SDK.

**Always run BEFORE `eas build`:**

```bash
cd mobile
npx expo@latest install --fix --legacy-peer-deps
npm install --legacy-peer-deps
```

If you forget this step, the build will likely fail in the
"Run fastlane → Compile Swift" phase with errors like:

> 'weak' must be a mutable variable, because it may change at runtime

That error is the Swift compiler telling us a package needs to be
updated to a version that supports the current Xcode's Swift version.
`expo install --fix` re-resolves every package to the version that the
current Expo SDK declares compatible with that Xcode.

After running it, commit the updated `package.json` and `package-lock.json`
back to GitHub so the fix is persistent.
