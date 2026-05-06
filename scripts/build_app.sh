#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
DIST_DIR="${ROOT_DIR}/dist"
APP_NAME="AareTempBar"

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

# Ad-hoc codesign (required for Gatekeeper)
echo "==> Ad-hoc signing ${APP_NAME}.app ..."
codesign --sign - --force --deep "${DIST_DIR}/${APP_NAME}.app"

echo ""
echo "Build complete: ${DIST_DIR}/${APP_NAME}.app"
