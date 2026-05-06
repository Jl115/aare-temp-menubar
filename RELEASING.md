# Releasing AareTempBar

## Prerequisites

### Developer ID Certificate

You need a valid **Developer ID Application** certificate in your keychain. This is a paid Apple Developer account certificate used to sign and notarize macOS apps for distribution outside the App Store.

1. Request a **Developer ID Application** certificate from the [Apple Developer Portal](https://developer.apple.com/account/resources/certificates/list).
2. Download and install it into your macOS keychain.
3. Note the exact identity name (e.g., `Developer ID Application: Your Name (TEAMID)`).

### App-Specific Password

For notarization, you need an App-Specific Password (not your Apple ID password):

1. Go to [appleid.apple.com](https://appleid.apple.com) > Sign-In and Security > App-Specific Passwords.
2. Generate a new password.
3. Save it securely.

## Local Build

Set environment variables before building:

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export NOTARIZATION_APPLE_ID="your-apple-id@example.com"
export NOTARIZATION_TEAM_ID="YOURTEAMID"
export NOTARIZATION_PASSWORD="your-app-specific-password"
```

Then build:

```bash
uv sync
./scripts/build_app.sh
open dist/AareTempBar.app
```

The build script will:

1. Build the `.app` bundle with PyInstaller
2. Sign it with your Developer ID certificate
3. Submit it to Apple for notarization
4. Staple the notarization ticket

The app will open without any Gatekeeper warnings on any user's machine.

## GitHub Actions CI/CD Release

### Required GitHub Secrets

Go to **Settings > Secrets and variables > Actions** in your repository and add:

| Secret                       | Description                                                   | How to Get                                                       |
| ---------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- |
| `CODESIGN_IDENTITY`          | Exact name of your Developer ID certificate.                  | `security find-identity -v -p codesigning`                       |
| `MACOS_CERTIFICATE`          | Base64-encoded `.p12` Developer ID certificate + private key. | Export from Keychain Access as `.p12`, then `base64 -i cert.p12` |
| `MACOS_CERTIFICATE_PASSWORD` | Password for the `.p12` file.                                 | Set when exporting from Keychain Access.                         |
| `NOTARIZATION_APPLE_ID`      | Your Apple ID email.                                          | `your-apple-id@example.com`                                      |
| `NOTARIZATION_TEAM_ID`       | Your Apple Developer Team ID.                                 | From Apple Developer Portal > Membership.                        |
| `NOTARIZATION_PASSWORD`      | App-Specific Password for notarization.                       | Generated at [appleid.apple.com](https://appleid.apple.com).     |

### Alternative: Notarization via Keychain Profile

Instead of `NOTARIZATION_PASSWORD`, you can use a stored keychain profile. Create it locally:

```bash
xcrun notarytool store-credentials --apple-id "your-apple-id@example.com" --team-id "YOURTEAMID"
```

Then set GitHub Secret `NOTARIZATION_KEYCHAIN_PROFILE` to the profile name.

### Release Steps

1. Update the version in `pyproject.toml`.
2. Commit and push.
3. Tag the release: `git tag v0.9.4`
4. Push the tag: `git push origin v0.9.4`
5. GitHub Actions will automatically:
   - Build the `.app` with PyInstaller
   - Sign it with your Developer ID certificate
   - Notarize it with Apple
   - Staple the notarization ticket
   - Package it into `AareTempBar-macos.zip`
   - Create a GitHub Release and attach the zip

## Homebrew Cask

After the CI finishes, copy the SHA256 of `AareTempBar-macos.zip` from the release page.

1. Update the Cask in `jl115/homebrew-aare` with the new version and SHA256.
2. Run `brew bump-cask-pr aare-temp-menubar` (or edit manually).

## Troubleshooting

### `Developer ID Application` not found

If you're building locally and get a "no identity found" error, first verify the certificate is in your keychain:

```bash
security find-identity -v -p codesigning
```

If missing, import it:

```bash
security import /path/to/cert.p12 -k ~/Library/Keychains/login.keychain-db -P "password" -T /usr/bin/codesign
```

### Notarization fails with "Invalid password"

Check that your App-Specific Password hasn't expired. Generate a new one at [appleid.apple.com](https://appleid.apple.com).
Also verify the `--team-id` matches the Team ID of the certificate used to sign the app.

### Gatekeeper still warns after download

Ensure `xcrun stapler staple` completed successfully in the build log. If the staple fails, the app is likely signed but not notarized, or there was a race condition. You can manually staple:

```bash
xcrun stapler staple dist/AareTempBar.app
```

