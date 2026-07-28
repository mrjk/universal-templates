#!/bin/bash
# snip: sync with: snip sync %FILE%
# snip: path=files/bin/shell/cli-app.bash ref=main
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=main

# TEMPLATE_VERSION=2026-07-28

# Basic bash template for command/resource based CLI.
# Features:
# * Automatic command discovery and help generation
# * Logging and traces
# * Application dependency checker
# * Support for getopts
# * Return code support
# * Command executor with dry mode
# * Environment variable support

set -euo pipefail

# App Global variable
# =================

# Global vars
APP_SCRIPT="${0##*/}"
APP_NAME="${APP_SCRIPT%.*}"

# Metadata vars
APP_AUTHOR="author"
APP_EMAIL="email@address.org"
APP_LICENSE="GPLv3"
APP_URL="https://github.com/$APP_AUTHOR/$APP_NAME"
APP_REPO="https://github.com/$APP_AUTHOR/$APP_NAME.git"
APP_GIT="git@github.com:$APP_AUTHOR/$APP_NAME.git"

APP_STATUS=alpha
APP_DATE="2026-07-09"
APP_VERSION=0.0.1


# CLI libraries
# =================
# Validate log level pass aginst limit
_log_validate_level ()
{
  local level=$1
  local limit_level=${2:-${APP_LOG_SCALE%%:*}}
  
  if [[ ! ":${APP_LOG_SCALE#*$limit_level:}:$limit_level:" =~ :"$level": ]]; then
    if [[ ! ":${APP_LOG_SCALE}" =~ :"$level": ]]; then
      >&2 printf "%s\n" "  BUG: Unknown log level: $level"
    fi
    return 1
  fi
}

# Logging support, with levels
_log() {
  local old_setting=${-//[^x]/}; set +x
  local level="${1:-DEBUG}"
  shift 1 || true

  # Check log level filter
  if _log_validate_level "$level" "${APP_LOG_LEVEL:-}"; then

    local msg=${*}
    if [[ "$msg" == '-' ]]; then
      msg="$(cat -)"
    fi
    while read -r -u 3 line; do
      >&2 printf "%6s: %s\\n" "$level" "${line:- }"
    done 3<<<"$msg"
  fi
  
  # Restore trace mode if was enabled
  if [[ -n "${old_setting-}" ]]; then set -x; else set +x; fi
}

# Terminate all with error message and rc code
_die ()
{
    local rc=${1:-1}
    shift 1 || true
    local msg="${*:-}"
    local prefix=QUIT
    [[ "$rc" -eq 0 ]] || prefix=DIE
    if [[ -z "$msg" ]]; then
      [ "$rc" -ne 0 ] || exit 0
      _log "$prefix" "Program terminated with error: $rc"
    else
      _log "$prefix" "$msg"
    fi

    # Remove EXIT trap and exit nicely
    trap '' EXIT
    exit "$rc"
}

# Run command with dry mode support
_exec ()
{
  local cmd=( "$@" )
  if ${APP_DRY:-false}; then
    _log DRY "  | ${cmd[@]}"
  else
    _log RUN "  | ${cmd[@]}"
    "${cmd[@]}"
  fi
}   

# Dump all application vars (debug)
# shellcheck disable=SC2120 # Argument is optional by default
_dump_vars ()
{
  local prefix=${1:-APP_}
  declare -p | grep " .. $prefix" >&2 || {
      >&2 _log WARN "No var starting with: $prefix"
  }
}

# Ensure a program is available
_check_bin ()
{
  local cmd cmds="${*:-}"
  for cmd in $cmds; do
    command -v "$1" >&/dev/null || return 1
  done
}

# Internal helper to show bash traces (debug)
# shellcheck disable=SC2120 # Argument is optional by default
_sh_trace ()
{
  local msg="${*}"

  (
    >&2 printf "%s\n" "TRACE: line, function, file"
    for i in {0..10}; do
      trace=$(caller "$i" 2>&1 || true )
      if [ -z "$trace" ] ; then
        continue
      else
        printf "%s\n" "$trace"
      fi
    done | tac | head -n -1
    [ -z "$msg" ] || >&2 printf "%s\n" "TRACE: Bash trace: $msg"
  )
}

# Internal function to catch errors
# Usage: trap '_sh_trap_error $? ${LINENO} trap_exit 42' EXIT
_sh_trap_error () {
    local rc=$1
    [[ "$rc" -ne 0 ]] || return 0
    local line="$2"
    local msg="${3-}"
    local code="${4:-1}"
    set +x

    _log ERR "Uncatched bug:"
    _sh_trace # | _log TRACE -
    if [[ -n "$msg" ]] ; then
      _log ERR "Error on or near line ${line}: ${msg}; got status ${rc}"
    else
      _log ERR "Error on or near line ${line}; got status ${rc}"
    fi
    exit "${code}"
}

# Extra libs
# =================

# Ask the user to confirm
# Usage:
#  [[ "${APP_FORCE}" == "true" ]] || continue=$(_confirm "Confirm to add new client ?")
_confirm () {
  local msg="${1:-Do you want to continue?}"
  >&2 printf "%s" "${1:-$msg}"
  >&2 printf "%s" "([y]es or [N]o): "
  >&2 read -n1 REPLY
  >&2 printf "\n"
  case $(tr '[A-Z]' '[a-z]' <<< "$REPLY" ) in
    y|yes) printf "%s\n" "true" ;;
    *)     printf "%s\n" "false" ;;
  esac
}

# Ask the user to input string
_input () {
  local msg="Please enter input:"
  local default=${2-}
  >&2 printf "%s" "${1:-$msg}${default:+ [$default]}: "
  >&2 read REPLY
  [[ -n "$REPLY" ]] || REPLY=${default}
  printf "%s\n" "$REPLY"
}

# Transform yaml to json
_yaml2json ()
{
  python3 -c 'import json, sys, yaml ; y = yaml.safe_load(sys.stdin.read()) ; print(json.dumps(y))'
}



# CLI helpers
# =================

# Dispatch command
clish_dispatch ()
{
  local prefix=$1
  local cmd=${2-}
  shift 2 || true
  [ ! -z "$cmd" ] || _die 3 "Missing command name, please check usage"

  if [[ $(type -t "${prefix}${cmd}") == function ]]; then
    "${prefix}${cmd}" "$@"
  else
    _log ERROR "Unknown command for ${prefix%%_?}: $cmd"
    return 3
  fi
}


# Parse command options
# Called function must return an args array with remaining args
clish_parse_opts ()
{
  local func=$1
  shift
  clish_dispatch "$func" _options "$@"
}

# Read CLI options for a given function/command
# Options must be in a case statement and surounded by
# 'parse-opt-start' and 'parse-opt-stop' strings. Returns
# a list of value separated by ,. Fields are:
clish_help_options ()
{
  local func=$1
  local data=

  # Check where to look options function
  if declare -f "${func}_options" >/dev/null; then
    func="${func}_options"
    data=$(declare -f "$func")
    data=$(printf "%s\n%s\n" 'parse-opt-start' "$data" )
  else
    data=$(declare -f "$func")
  fi

  # declare -f ${func} \
  echo "$data" | awk '/parse-opt-start/,/parse-opt-stop/ {print}' \
    | grep --no-group-separator -A 1 -E '^ *--?[a-zA-Z0-9].*)$' \
    | sed -E '/\)$/s@[ \)]@@g;s/.*: "//;s/";//' \
    | xargs -n2 -d'\n' \
    | sed 's/ /,/;/^$/d'
}

# List all available commands starting with prefix
clish_help_subcommands ()
{
  local prefix=${1:-cli__}
  declare -f \
    | grep -E -A 2 '^'"$prefix"'[a-z0-9]*(__[a-z0-9]*)*? \(\)' \
    | sed '/{/d;/--/d;s/'"$prefix"'//;s/ ()/,/;s/";$//;s/^  *: "//;' \
    | xargs -n2 -d'\n' \
    | sed 's/, */,/;s/__/ /g;/,,$/d'
}

# Show help message of a function
clish_help_msg ()
{
  local func=$1
  clish_dispatch "$func" _usage 2>/dev/null || true
}


# Show cli usage for a given command
clish_help ()
{
  : ",Show this help"
  local func=${1:-cli}
  local commands= options= message= output=

  # Help message
  message=$(clish_help_msg $func)

  # Fetch command options
  options=$(
    while IFS=, read -r flags meta desc _; do
      if [ ! -z "${flags:-}" ]; then
        printf "  %-16s  %-20s  %s\n" "$flags" "$meta" "$desc"
      fi
    done <<< "$(clish_help_options $func)"
  )

  # Fetch sub command informations
  commands=$(
    while IFS=, read -r flags meta desc _; do
      if [ ! -z "${flags:-}" ]; then
        printf "  %-16s  %-20s  %s\n" "$flags" "$meta" "$desc"
      fi
    done <<< "$(clish_help_subcommands ${func}__)"
  )

  # Display help message
  printf "%s\n" "${message:+$message}
${commands:+
commands:
$commands}
${options:+
options:
$options
}"

  # Append extra infos
  if ! [[ "$func" == *"_"* ]]; then
    cat <<EOF
info:
  author: $APP_AUTHOR ${APP_EMAIL:+<$APP_EMAIL>}
  version: ${APP_VERSION:-0.0.1}-${APP_STATUS:-beta}${APP_DATE:+ ($APP_DATE)}
  license: ${APP_LICENSE:-MIT}
EOF
  fi

}


# CLI Commands
# =================

cli__example ()
{
  : "[ARG],Example command"

  local arg=${1:-Without options}
  echo "Called command: example $arg"
}

# >>> snip:slot=commands
# <<< snip:slot=commands


# CLI Sub Commands
# =================

# Display help message
cli__group_usage ()
{
  cat <<EOF
${APP_NAME}: Manage groups (Subcommand example)

usage: ${APP_NAME} group [OPTS] add NAME
       ${APP_NAME} group [OPTS] rm NAME
       ${APP_NAME} group help
EOF
}

# Read CLI options, shows group level options
cli__group_options ()
{
  while [[ ! -z "${1:-}" ]]; do
    # : "parse-opt-start"
    case "$1" in
      -h|--help|help)
        : ",Show help"
        clish_help cli__group; _die 0
        ;;
      -a|--all)
        : ",Select all"
        mode=all
        shift
        ;;
      -m|--message)
        : "MSG,Define message"
        [[ ! -z "${2:-}" ]] || _die 1 "Missing message"
        msg=$2
        shift 2
        ;;
      -*)
        _die 1 "Unknown option: $1"
        ;;
      # Options and arguments can be mixed
      *)
        args+=("$1")
        shift 1
      # Options always first
      # *)
      #   args=("$@")
      #   shift $#
      # ;;
    esac
    # : "parse-opt-stop"
  done
}

cli__group ()
{
  : "COMMAND,Manage groups"

  # Set default vars
  local msg="Default message"
  local mode="limited"

  # Parse args
  local args=()
  clish_parse_opts cli__group "$@"
  set -- "${args[@]}"

  # report to user
  _log INFO "Requested mod: $mode"
  _log INFO "Requested message: $msg"

  # Dispatch to sub commands
  clish_dispatch cli__group__ "$@" || _die $?
}


# Basic simple level sub-commands
# ---------------
cli__group__add()
{
  : "NAME [OPTS],Add subcommand"
  echo "Add: '$1' in '$mode' mode with message: '$msg'"
}

cli__group__rm()
{
  : "NAME,Remove subcommand"
  echo "Remove: $1"
}


# Nested command names
# ---------------
cli__group__var ()
{
  : "," # Ignored from help
  clish_dispatch cli__group__var__ "$@" \
    || _die $? "Group command failed with error: $?" 
}

cli__group__var__get()
{
  : "VAR,Get variable"
  echo "Value of var $1 is current date: $(date)"
}

cli__group__var__set()
{
  : "VAR VALUE,Set variable value"
  local name=$1
  shift
  [ $# -gt 0 ] || return 42
  echo "Value of var '$name' set to: $@"
}


# Core App
# =================

# Check if all required bin are available in PATH
cli_require ()
{
  local deps=${@:-${APP_DEPENDENCIES:-}}

  local prog=
  for prog in ${deps-} ; do
    _check_bin $prog || {
      _die 2 "Can't find '$prog', please install it first"
    }
  done
}

# App help message
cli_usage ()
{
  cat <<EOF
${APP_NAME} is a nice command line tool.

usage: ${APP_NAME} [OPTS] <COMMAND> [ARGS]
       ${APP_NAME} --help
EOF
}

# Parse CLI options
cli_options ()
{
  while [[ ! -z "${1:-}" ]]; do
    # : "parse-opt-start"
    case "$1" in
      -h|--help)
        : ",Show this help message"
        args=( "help" "$@" )
        shift
        ;;
      -n|--dry)
        : ",Enable dry mode"
        _log INFO "Dry mode enabled"
        APP_DRY=true 
        shift
        ;;
      -f|--force)
        : ",Enable force mode"
        _log INFO "Force mode enabled"
        APP_FORCE=true 
        shift
        ;;
      -x | --xtrace)
        : ",Show debug traces"
        shift
        set -x
        ;;
      -v|-vv|-vvv)
        : "[LEVEL],Set verbosity level"
        if [[ -n "${2:-}" ]] && _log_validate_level "${2:-}" 2>/dev/null; then
          APP_LOG_LEVEL="$2"
          shift
        elif [[ "$1" == "-v" ]]; then
          APP_LOG_LEVEL=INFO
        elif [[ "$1" == "-vv" ]]; then
          APP_LOG_LEVEL=DEBUG
        else
          _log DEBUG "Max logging enabled"          
          APP_LOG_LEVEL=TRACE
        fi
        shift
        _log INFO "Log level set to: $APP_LOG_LEVEL"
        ;;
      -V|--version)
        : ",Show version"
        echo "$APP_VERSION"
        exit 0
        ;;
      -*)
        _die 1 "Unknown option: $1"
        ;;
      # Options and arguments can be mixed
      *)
      # Parse all options after first arg
        #args+=("$1")
        #shift 1
      # Options always first
        args=( "$@" )
        shift $#
      ;;
    esac
    # : "parse-opt-stop"
  done
}

# App initialization
cli_init ()
{
  # Useful shortcuts
  export VCS_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
  export SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  export WORK_DIR=${VCS_DIR:-${SCRIPT_DIR:-$PWD}}
  export PWD_DIR=${PWD}
}

# Main entrypoint
cli ()
{
  # Init
  trap '_sh_trap_error $? ${LINENO} trap_exit 42' EXIT
  
  # Cli configuration  
  APP_DRY=${APP_DRY:-false}
  APP_FORCE=${APP_FORCE:-false}
  APP_LOG_LEVEL=${APP_LOG_LEVEL:-NOTICE}  # DRY, DEBUG, TRACE
  APP_LOG_SCALE="TRACE:DEBUG:RUN:INFO:DRY:HINT:NOTICE:CMD:USER:WARN:ERR:ERROR:CRIT:TODO:DIE:QUIT:PROMPT"

  # Automatic vars
  APP_IS_INTERACTIVE=${APP_IS_INTERACTIVE:-$([ -t 0 ] && echo true || echo false)}
  SCRIPT_REAL_PATH=$(realpath "$0")
  SCRIPT_REAL_DIR=$( cd -- "$( dirname -- "$SCRIPT_REAL_PATH" )" &> /dev/null && pwd )
  APP_REAL_NAME=$(basename "$SCRIPT_REAL_PATH")
  APP_CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/$APP_REAL_NAME

  # App Configuration
  # ...

  # Parse CLI flags
  local args=()
  clish_parse_opts cli "$@"
  set -- "${args[@]}"

  # Init app
  cli_init

  # Route commands before requirements
  local cmd=${1:-help}
  shift 1 || true
  case "$cmd" in
    -h|--help|help|h) clish_help cli; _die 0 ;;
  esac
  
  # Check requirements
  cli_require 

  # Dispatch subcommand
  clish_dispatch cli__ "$cmd" "$@" \
    || _die $? "Command '$cmd' returned error: $?"  
}

cli "${@}"
