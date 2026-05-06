#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
DIST_DIR="${ROOT_DIR}/dist"
APP_NAME="AareTempBar"
APP_PATH="${DIST_DIR}/${APP_NAME}.app"
IDENTITY="${CODESIGN_IDENTITY:-}"
ENTITLEMENTS="${ROOT_DIR}/AareTempBar.entitlements"

APPLE_ID="${NOTARIZATION_APPLE_ID:-}"
TEAM_ID="${NOTARIZATION_TEAM_ID:-}"
NOTARIZATION_PASSWORD="${NOTARIZATION_PASSWORD:-}"
KEYCHAIN_PROFILE="${NOTARIZATION_KEYCHAIN_PROFILE:-}"

echo "==> Building ${APP_NAME}.app ..."

# Ensure venv exists
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Error: .venv not found. Run 'uv sync' first."
    exit 1
fi

# Install pyinstaller into the venv if missing
if ! "${VENV_DIR}/bin/python" -c "import PyInstaller" 2>/dev/null; then
    echo "==> Installing pyinstaller ..."
    uv pip install pyinstaller
fi

# Clean previous build
rm -rf "${DIST_DIR}" "${ROOT_DIR}/build"

# Build the app bundle
cd "${ROOT_DIR}"
"${VENV_DIR}/bin/pyinstaller" "AareTempBar.spec" --clean --noconfirm

# Signing
if [[ -n "${IDENTITY}" ]]; then
    echo "==> Signing ${APP_NAME}.app with '${IDENTITY}' ..."
    codesign --sign "${IDENTITY}" \
        --entitlements "${ENTITLEMENTS}" \
        --force --deep --options runtime \
        "${APP_PATH}"

    echo "==> Verifying signature ..."
    codesign --verify --deep --strict --verbose=2 "${APP_PATH}"
else
    echo "==> Ad-hoc signing ${APP_NAME}.app ..."
    codesign --sign - --force --deep "${APP_PATH}"
    echo "==> WARNING: No Developer ID certificate found. App will not be distributable."
    exit 0
fi

# Notarization
echo "==> Preparing notarization bundle ..."
rm -f "${DIST_DIR}/${APP_NAME}.zip"
ditto -c -k --keepParent "${APP_PATH}" "${DIST_DIR}/${APP_NAME}.zip"

if [[ -n "${KEYCHAIN_PROFILE}" ]]; then
    echo "==> Submitting to Apple for notarization (keychain profile) ..."
    xcrun notarytool submit "${DIST_DIR}/${APP_NAME}.zip" \
        --keychain-profile "${KEYCHAIN_PROFILE}" \
        --wait
elif [[ -n "${NOTARIZATION_PASSWORD}" && -n "${APPLE_ID}" && -n "${TEAM_ID}" ]]; then
    echo "==> Submitting to Apple for notarization (app-specific password) ..."
    xcrun notarytool submit "${DIST_DIR}/${APP_NAME}.zip" \
        --apple-id "${APPLE_ID}" \
        --team-id "${TEAM_ID}" \
        --password "${NOTARIZATION_PASSWORD}" \
        --wait
else
    echo ""
    echo "⚠️  Notarization credentials not configured."
    echo "    To enable notarization, set one of the following:"
    echo "      - NOTARIZATION_KEYCHAIN_PROFILE (created via notarytool store-credentials)"
    echo "      - NOTARIZATION_PASSWORD + NOTARIZATION_APPLE_ID + NOTARIZATION_TEAM_ID"
    exit 0
fi

echo "==> Stapling notarization ticket to ${APP_NAME}.app ..."
xcrun stapler staple "${APP_PATH}"

echo "==> Validating staple ..."
xcrun stapler validate "${APP_PATH}"

echo ""
echo "✅ Build complete: ${APP_PATH}"
echo "✅ Notarized and stapled!"
