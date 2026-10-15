#!/usr/bin/env bash
# setup.sh — install Blender 4.5 LTS (headless) for blender-for-muse
#
#   ./setup.sh          download + install Blender, then verify
#   ./setup.sh check    verify an existing install (re-run safe)
#
# Env overrides:
#   BLENDER_VERSION     e.g. 4.5.14        (default 4.5.14)
#   BLENDER_DIR         install root       (default $HOME/tools/blender)
#
# The binary ends up at:
#   $BLENDER_DIR/blender-<version>-linux-x64/blender
# plus a version-independent stable symlink:
#   $BLENDER_DIR/current/blender   <-- point the skill at this one
# Point the skill at it via $BLENDER_BIN, or use the default path above.
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-4.5.14}"
INSTALL_ROOT="${BLENDER_DIR:-$HOME/tools/blender}"
TARBALL="blender-${BLENDER_VERSION}-linux-x64.tar.xz"
URL="https://download.blender.org/release/Blender4.5/${TARBALL}"
VERSION_DIR="$INSTALL_ROOT/blender-${BLENDER_VERSION}-linux-x64"
BIN="$VERSION_DIR/blender"
# Stable path that never changes across versions:
STABLE_BIN="$INSTALL_ROOT/current/blender"

link_current() {
  # Point "current" at the installed version dir (atomic-ish, re-run safe)
  ln -sfn "blender-${BLENDER_VERSION}-linux-x64" "$INSTALL_ROOT/current"
}

check() {
  # Prefer the stable symlink; fall back to the versioned dir
  for candidate in "$STABLE_BIN" "$BIN"; do
    if [[ -x "$candidate" ]]; then
      echo "OK: $candidate"
      "$candidate" -b --version | head -2
      return 0
    fi
  done
  echo "MISSING: $STABLE_BIN"
  return 1
}

if [[ "${1:-}" == "check" ]]; then
  check
  exit $?
fi

if check >/dev/null 2>&1; then
  echo "Blender already installed."
  link_current   # make sure the stable symlink exists
  check
  exit 0
fi

echo "Installing Blender ${BLENDER_VERSION} -> ${INSTALL_ROOT}"
mkdir -p "$INSTALL_ROOT"
cd "$INSTALL_ROOT"

if [[ ! -f "$TARBALL" ]]; then
  echo "Downloading ${URL} (~400MB)..."
  if command -v curl >/dev/null; then
    curl -fL -o "$TARBALL" "$URL"
  elif command -v wget >/dev/null; then
    wget -O "$TARBALL" "$URL"
  else
    echo "ERROR: need curl or wget" >&2
    exit 1
  fi
fi

echo "Extracting..."
tar -xf "$TARBALL"
link_current

echo "Verifying headless run..."
check
echo
echo "Done."
echo "Stable binary path (version-independent): $STABLE_BIN"
echo "Tip: export BLENDER_BIN=\"\$HOME/tools/blender/current/blender\""
