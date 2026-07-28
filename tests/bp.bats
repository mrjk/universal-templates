#!/usr/bin/env bats
# bats tests for bin/bp — all against a local git repo (no network)

setup_file() {
  export REPO_ROOT
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
  export BP="$REPO_ROOT/bin/bp"
  export FIXTURE_REPO
  FIXTURE_REPO="$(mktemp -d)"
  export CONSUMER
  CONSUMER="$(mktemp -d)"

  # Build a minimal boilerplate fixture repo with one part we can mutate for updates.
  mkdir -p "$FIXTURE_REPO/parts/python/demo/files/subdir"
  cat > "$FIXTURE_REPO/parts/python/demo/part.yaml" <<'EOF'
name: demo
description: "demo part for tests"
language: python
files_dir: files
EOF
  echo "version-1" > "$FIXTURE_REPO/parts/python/demo/files/demo.txt"
  echo "nested-1" > "$FIXTURE_REPO/parts/python/demo/files/subdir/nested.txt"

  mkdir -p "$FIXTURE_REPO/parts/shell/other/files"
  cat > "$FIXTURE_REPO/parts/shell/other/part.yaml" <<'EOF'
name: other
description: "second part"
language: shell
files_dir: files
EOF
  echo "other-content" > "$FIXTURE_REPO/parts/shell/other/files/other.txt"

  mkdir -p "$FIXTURE_REPO/common/sample/files"
  cat > "$FIXTURE_REPO/common/sample/part.yaml" <<'EOF'
name: sample
description: "common sample"
language: common
files_dir: files
EOF
  echo "sample" > "$FIXTURE_REPO/common/sample/files/sample.cfg"

  mkdir -p "$FIXTURE_REPO/templates/python"
  echo "placeholder" > "$FIXTURE_REPO/templates/python/copier.yml"

  git -C "$FIXTURE_REPO" init -q -b main
  git -C "$FIXTURE_REPO" config user.email "test@example.com"
  git -C "$FIXTURE_REPO" config user.name "Test"
  git -C "$FIXTURE_REPO" add -A
  git -C "$FIXTURE_REPO" commit -q -m "initial fixture"
}

teardown_file() {
  rm -rf "$FIXTURE_REPO" "$CONSUMER"
}

setup() {
  # Fresh consumer project per test
  rm -rf "$CONSUMER"
  mkdir -p "$CONSUMER"
  cd "$CONSUMER"
}

@test "bp --help prints usage" {
  run "$BP" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"bp add"* ]]
}

@test "bp add installs files at project root and writes state" {
  run "$BP" add "$FIXTURE_REPO" parts/python/demo
  [ "$status" -eq 0 ]
  [ -f "$CONSUMER/demo.txt" ]
  [ -f "$CONSUMER/subdir/nested.txt" ]
  [ -f "$CONSUMER/.bp/demo.json" ]
  run jq -r .name "$CONSUMER/.bp/demo.json"
  [ "$output" = "demo" ]
  run jq -r '.installed_files | length' "$CONSUMER/.bp/demo.json"
  [ "$output" = "2" ]
  run jq -r .sha "$CONSUMER/.bp/demo.json"
  [ -n "$output" ]
  [ "$output" != "null" ]
}

@test "bp add refuses overwrite without -y" {
  echo "existing" > "$CONSUMER/demo.txt"
  run "$BP" add "$FIXTURE_REPO" parts/python/demo
  [ "$status" -ne 0 ]
  [[ "$output" == *"refusing to overwrite"* ]] || [[ "$stderr" == *"refusing to overwrite"* ]]
}

@test "bp update shows diff and applies with -y" {
  "$BP" add "$FIXTURE_REPO" parts/python/demo
  local old_sha
  old_sha=$(jq -r .sha "$CONSUMER/.bp/demo.json")

  # Mutate consumer copy so a diff appears even before fixture change
  echo "local-edit" > "$CONSUMER/demo.txt"

  # Also bump fixture and commit so remote content changes
  echo "version-2" > "$FIXTURE_REPO/parts/python/demo/files/demo.txt"
  git -C "$FIXTURE_REPO" add -A
  git -C "$FIXTURE_REPO" commit -q -m "bump demo"

  run "$BP" update demo -y
  [ "$status" -eq 0 ]
  [[ "$output" == *"diff for demo"* ]] || [[ "$output" == *"updated"* ]]
  run cat "$CONSUMER/demo.txt"
  [ "$output" = "version-2" ]
  local new_sha
  new_sha=$(jq -r .sha "$CONSUMER/.bp/demo.json")
  [ "$new_sha" != "$old_sha" ]
}

@test "bp remove deletes installed files and state" {
  "$BP" add "$FIXTURE_REPO" parts/python/demo
  [ -f "$CONSUMER/demo.txt" ]
  run "$BP" remove demo -y
  [ "$status" -eq 0 ]
  [ ! -f "$CONSUMER/demo.txt" ]
  [ ! -f "$CONSUMER/subdir/nested.txt" ]
  [ ! -f "$CONSUMER/.bp/demo.json" ]
}

@test "bp list renders tree for multiple parts" {
  "$BP" add "$FIXTURE_REPO" parts/python/demo
  "$BP" add "$FIXTURE_REPO" parts/shell/other
  run "$BP" list
  [ "$status" -eq 0 ]
  [[ "$output" == *"demo"* ]]
  [[ "$output" == *"other"* ]]
  [[ "$output" == *"├─"* ]] || [[ "$output" == *"└─"* ]]
}

@test "bp browse lists parts and common without installing" {
  run "$BP" browse "$FIXTURE_REPO"
  [ "$status" -eq 0 ]
  [[ "$output" == *"parts/python/demo"* ]]
  [[ "$output" == *"parts/shell/other"* ]]
  [[ "$output" == *"common/sample"* ]]
  [[ "$output" == *"templates/python"* ]]
  [ ! -f "$CONSUMER/demo.txt" ]
}

@test "missing jq produces clear error" {
  local fakedir
  fakedir=$(mktemp -d)
  # Minimal PATH: git + shell utilities, but no jq
  ln -s "$(command -v git)" "$fakedir/git"
  ln -s "$(command -v bash)" "$fakedir/bash"
  for cmd in mkdir mktemp cp rm ls find date dirname basename sed head cat diff rmdir tr sort uname; do
    if command -v "$cmd" >/dev/null 2>&1; then
      ln -s "$(command -v "$cmd")" "$fakedir/$cmd"
    fi
  done
  run env PATH="$fakedir" "$BP" list
  local status=$status
  local combined="$output$stderr"
  rm -rf "$fakedir"
  [ "$status" -ne 0 ]
  [[ "$combined" == *"jq is required"* ]]
}

@test "missing git produces clear error" {
  local fakedir
  fakedir=$(mktemp -d)
  ln -s "$(command -v jq)" "$fakedir/jq"
  ln -s "$(command -v bash)" "$fakedir/bash"
  for cmd in mkdir mktemp cp rm ls find date dirname basename sed head cat diff rmdir tr sort uname; do
    if command -v "$cmd" >/dev/null 2>&1; then
      ln -s "$(command -v "$cmd")" "$fakedir/$cmd"
    fi
  done
  run env PATH="$fakedir" "$BP" list
  local status=$status
  local combined="$output$stderr"
  rm -rf "$fakedir"
  [ "$status" -ne 0 ]
  [[ "$combined" == *"git is required"* ]]
}

@test "bp add fails on missing part path" {
  run "$BP" add "$FIXTURE_REPO" parts/python/does-not-exist
  [ "$status" -ne 0 ]
}

@test "bp update fails for unknown part" {
  run "$BP" update nope -y
  [ "$status" -ne 0 ]
  [[ "$output" == *"no installed part"* ]] || [[ "$stderr" == *"no installed part"* ]]
}
