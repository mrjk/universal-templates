#!/usr/bin/env bash
# install.sh — install bp onto PATH (~/.local/bin/bp)
set -euo pipefail

INSTALL_DIR="${BP_INSTALL_DIR:-$HOME/.local/bin}"
INSTALL_PATH="$INSTALL_DIR/bp"
REPO_URL="${BP_INSTALL_REPO:-}"
REF="${BP_INSTALL_REF:-main}"

die() { echo "error: $*" >&2; exit 1; }

need() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required to install and run bp"
}

need git
need jq

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC=""

if [ -f "$SCRIPT_DIR/bin/bp" ]; then
  SRC="$SCRIPT_DIR/bin/bp"
else
  need curl
  if [ -z "$REPO_URL" ]; then
    die "set BP_INSTALL_REPO to a git URL (or run install.sh from a clone of this repo)"
  fi
  tmp=$(mktemp -d)
  cleanup() { rm -rf "$tmp"; }
  trap cleanup EXIT
  git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$REF" "$REPO_URL" "$tmp" \
    || die "failed to clone $REPO_URL"
  git -C "$tmp" sparse-checkout set bin \
    || die "failed to sparse-checkout bin/"
  SRC="$tmp/bin/bp"
  [ -f "$SRC" ] || die "bin/bp not found in $REPO_URL@$REF"
fi

mkdir -p "$INSTALL_DIR"
cp "$SRC" "$INSTALL_PATH"
chmod +x "$INSTALL_PATH"

echo "installed: $INSTALL_PATH"

case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *)
    cat <<EOF

note: $INSTALL_DIR is not on your PATH.
Add this to your shell rc (~/.bashrc or ~/.zshrc):

  export PATH="\$HOME/.local/bin:\$PATH"

Then reload your shell or run: hash -r
EOF
    ;;
esac

echo "try: bp --help"
