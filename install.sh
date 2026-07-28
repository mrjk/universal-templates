#!/usr/bin/env bash
# install.sh — install bp onto PATH (~/.local/bin/bp)
set -euo pipefail

INSTALL_DIR="${BP_INSTALL_DIR:-$HOME/.local/bin}"
INSTALL_PATH="$INSTALL_DIR/bp"
REPO_URL="${BP_INSTALL_REPO:-}"
REF="${BP_INSTALL_REF:-main}"
SRC=""

die() { echo "error: $*" >&2; exit 1; }

need() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required to install and run bp"
}

script_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

cleanup_tmp() {
  rm -rf "${INSTALL_TMP:-}"
}

resolve_src() {
  local script_dir=$1
  if [ -f "$script_dir/bin/bp" ]; then
    SRC="$script_dir/bin/bp"
    return 0
  fi

  need curl
  if [ -z "$REPO_URL" ]; then
    die "set BP_INSTALL_REPO to a git URL (or run install.sh from a clone of this repo)"
  fi
  INSTALL_TMP=$(mktemp -d)
  trap cleanup_tmp EXIT
  git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$REF" "$REPO_URL" "$INSTALL_TMP" \
    || die "failed to clone $REPO_URL"
  git -C "$INSTALL_TMP" sparse-checkout set bin \
    || die "failed to sparse-checkout bin/"
  SRC="$INSTALL_TMP/bin/bp"
  [ -f "$SRC" ] || die "bin/bp not found in $REPO_URL@$REF"
}

install_bp() {
  mkdir -p "$INSTALL_DIR"
  cp "$SRC" "$INSTALL_PATH"
  chmod +x "$INSTALL_PATH"
  echo "installed: $INSTALL_PATH"
}

warn_if_not_on_path() {
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
}

main() {
  need git
  need jq
  resolve_src "$(script_dir)"
  install_bp
  warn_if_not_on_path
  echo "try: bp --help"
}

main "$@"
