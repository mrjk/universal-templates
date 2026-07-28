#!/bin/bash
# TEMPLATE_VERSION=2023-10-19

# Basic bash template for command/resource based CLI.
# Features:
# * Automatic command discovery and help generation
# * Logging and traces
# * Application dependency checker
# * Support for getopts
# * Return code support
# * Command executor with dry mode


# Add at the very bottom of your script
#  #!/bin/bash
#  # <your code>
#  # Import live clish (must stay at the end)
#  CLISH_URL='https://gist.githubusercontent.com/mrjk/775a53666fa10a5f40cc9297c5cbf835/raw/55ba7997f411119f3ee8f9d592ab25cd5523d9b4/clish.bash'
#  CLISH_LIB=/tmp/clish-$(id -u)
#  . $CLISH_LIB 2>/dev/null || { curl -s "$CLISH_URL" -o $CLISH_LIB && . $CLISH_LIB ; }
#  clish_init "$@"


set -eu

# App Global variable
# =================

APP_FILE="${0##*/}"
APP_NAME="${APP_FILE%%.*}"

APP_DESC="Command line tool to run stuffs"
APP_AUTHOR="author"
APP_EMAIL="email@address.org"
APP_LICENSE="GPLv3"
APP_URL="https://github.com/$APP_AUTHOR/$APP_NAME"

APP_STATUS=alpha
APP_DATE="2024-03-30"
APP_VERSION=0.0.1

#APP_DEPENDENCIES="column tree htop"
APP_LOG_SCALE="TRACE:DEBUG:RUN:INFO:DRY:HINT:NOTICE:CMD:USER:WARN:ERR:ERROR:CRIT:TODO:DIE"

APP_DRY=${APP_DRY:-false}
APP_FORCE=${APP_FORCE:-false}
APP_LOG_LEVEL=INFO
#APP_LOG_LEVEL=DRY
#APP_LOG_LEVEL=DEBUG


# CLI libraries
# =================


_script_log ()
{
  local lvl="${1:-DEBUG}"
  shift 1 || true

  # Check log level filter
  if [[ ! ":${APP_LOG_SCALE#*"$APP_LOG_LEVEL":}:$APP_LOG_LEVEL:" =~ :"$lvl": ]]; then
    if [[ ! ":${APP_LOG_SCALE}" =~ :"$lvl": ]]; then
      >&2 echo "  BUG: Unknown log level: $lvl"
    else
      return 0
    fi
  fi

  local msg=${*}
  if [[ "$msg" == '-' ]]; then
    msg="$(cat - )"
  fi
  while read -r -u 3 line ; do
    >&2 printf "%5s: %s\\n" "$lvl" "${line:- }"
  done 3<<<"$msg"
}


_script_die ()
{
    local rc=${1:-1}
    shift 1 || true
    local msg="${*:-}"
    if [[ "$rc" != 0 ]]; then    
      if [[ -z "$msg" ]]; then
          _script_log DIE "Program terminated with error: $rc"
      else
          _script_log DIE "$msg"
      fi
    fi

    # Remove EXIT trap and exit nicely
    trap '' EXIT
    exit "$rc"
}

_script_exec ()
{
  local cmd=( "$@" )
  if ${APP_DRY:-false}; then
    _script_log DRY "  | ${cmd[*]}"
  else
    _script_log RUN "  | ${cmd[*]}"
    "${cmd[@]}"
  fi
}   


# shellcheck disable=SC2120 # Argument is optional by default
_script_debug_vars ()
{
  local prefix=${1:-APP_}
  declare -p | grep " .. $prefix" >&2 || {
      >&2 _script_log WARN "No var starting with: $prefix"
  }
}

# Debug parameters
# USage: _script_debug_args "$@" 
_script_debug_args ()
{
  for ((i = 1; i <= $#; i++ )); do
    printf '%s\n' "Arg $i: ${!i}"
  done 
}

_script_has_command ()
{
  local cmd cmds="${*:-}"
  for cmd in $cmds; do
    command -v "$1" >&/dev/null || return 1
  done
}

# shellcheck disable=SC2120 # Argument is optional by default
_sh_trace ()
{
  local msg="${*}"

  (
    >&2 echo "TRACE: line, function, file"
    for i in {0..10}; do
      trace=$(caller "$i" 2>&1 || true )
      if [ -z "$trace" ] ; then
        continue
      else
        echo "$trace"
      fi
    done | tac
    [ -z "$msg" ] || >&2 echo "TRACE: Bash trace: $msg"
  )
}

# Usage: trap '_sh_trap_error $? ${LINENO} trap_exit 42' EXIT
_sh_trap_error () {
    local rc=$1
    [[ "$rc" -ne 0 ]] || return 0
    local line="$2"
    local msg="${3-}"
    local code="${4:-1}"
    set +x

    _script_log ERR "Uncatched bug:"
    _sh_trace
    if [[ -n "$msg" ]] ; then
      _script_log ERR "Error on or near line ${line}: ${msg}; got status ${rc}"
    else
      _script_log ERR "Error on or near line ${line}; got status ${rc}"
    fi
    exit "${code}"
}


# Clish helpers
# =================


# Retrieve function metadata
# Usage for single var with default value
#  optargs=$(_script_fnmeta "$func" optargs || echo MISSING)
# Usage in array:
#  IFS=$'\n' tmp=( $(_script_fnmeta test_func var3 meta2 var3) )
#  set -- "${tmp[@]}"
_script_fnmeta ()
{
  local func=$1
  shift 1
  local data=

  data=$(declare -f "$func" \
    | sed -En 's/    : "//p' \
    | sed -E 's/";?//' \
    | grep -E '^[a-z0-9_]+=' )

  if [[ -z "${data}" ]]; then
    # Always fail if empty
    return 1
  elif [[ -n "${*}" ]]; then
    for var in "$@"; do
      # We use grep to fail if var is not found
      grep -q "^$var=" <<< "$data" \
        && sed -En "/^$var=/s/^$var=//p" <<< "$data"
    done
  else
    # Make parsable bash code
    sed "s/^/fn_/;s/=/='/;s/$/'/" <<< "$data"
  fi
}



# List all cli commands starting with prefix
clish_list_cmds ()
{
  local prefix=${1:-cli__}
  declare -f | sed -E -n "s/$prefix([a-z0-9_]*) *\(\).*/\1/p" | tr '\n' ':'
}

# Load a clish command
# Usage:
#   clish_parse_cmd PREFIX CMD ARGS...
clish_parse_cmd ()
{
  local prefix=$1
  local cmd=$2
  shift 2 2>/dev/null || true
  local commands=

  # Search and prepare command to run 
  commands=$(clish_list_cmds cli__)
  if [[ ":$commands:" =~ .*":${cmd}:".* ]] ; then
    "cli__${cmd}" "${@}" || {
      _script_die $? "Command returned error: $?"  
    }
  else
    _script_die 3 "Unknown command: $cmd"
  fi
}




# Parse options with getopts
# Return a new global array ARGS
# Usage:
#   clish_parse_getopts FUNCTION "$@"
#   set -- "${ARGS[@]}"

clish_parse_getopts ()
{
  local func=$1 optargs=
  shift 1
  declare -g ARGS=("$@")

  # Ensure optargs is correctly defined on target function
  optargs=$(_script_fnmeta "$func" optargs) \
    || _script_die 4 "BUG: Missing meta 'optargs=$optargs' for '$func'"

  # Read CLI options with getopts
  local OPTIND OPTFLAG
  while getopts "$optargs" OPTFLAG 2>/dev/null; do
    # shellcheck disable=SC2086
    $func "${ARGS[@]}"
  done

  # Remove consumed args
  ARGS=("${ARGS[@]:($OPTIND-1)}")
}


declare -g APP_INIT=0
# Handle app initialization. Call with one of: 
# clish_init ${*:-}
# clish_init "${@}"
# DEfault hooks:
# - app_arg_parser: Parse args
# - app_init: Code to run on init
# - cli__<NAME>: Command to implement
clish_init ()
{

  # Avoid duplicate init
  [[ "${APP_INIT:-0}" == 0 ]] || return 0 
  declare -g APP_INIT=1 

  # Add error trap
  trap '_sh_trap_error $? ${LINENO} trap_exit 42' EXIT
  # _script_debug_args "$@" 
 
  clish_parse_getopts app__init__getopts "$@"
  # shellcheck disable=SC2068
  set -- "${ARGS[@]}"

  # Route commands before requirements
  local cmd=${1:-help}
  shift 1 || true
  case "$cmd" in
    -h|--help|help) cli__help; return ;;
  esac
  
  # Init app
  if [[ $(type -t app__init) == function ]]; then 
    app__init
  fi

  # Check requirements
  local prog
  for prog in ${APP_DEPENDENCIES-} ; do
    _script_has_command "$prog" || {
      _script_die 2 "Command '$prog' must be installed first"
    }
  done

  # Load app
  clish_parse_cmd __cli "$cmd" "$@"
}


# Default commands
# =================


# Show getop usage from function case structure
clish_usage_getopts ()
{
  local func=$1

  # Ensure optargs is correctly defined on target function
  _script_fnmeta "$func" optargs >/dev/null ||  _script_die 4 "BUG: Missing meta 'optargs=$optargs' for '$func'"

  declare -f "$func" \
    | grep -A 1 '^        .*)$' \
    | xargs | sed -E 's/\s?--\s?/\n/g' \
    | grep ') : ' \
    | sed -E 's/\) : /,/;s/;$//;s/$/\x0/' \
    | {
      while IFS="," read -r name value desc ; do
        printf "  %-30s %s\n" "-$name ${value:+ $value}" "$desc"
      done #< <(cat -)
    }
}

# Return all comand usage starting with pattern 
clish_usage_cmd_prefix ()
{
  local prefix=${1:-cli__} cmds=

  cmds=$(clish_list_cmds cli__ )
  for func in ${cmds//:/ }; do
    local fn_args='' fn_help='' cmd_name=${func#"$prefix"}
    eval "$(_script_fnmeta "cli__$func")"
    printf "  %-30s %s\n" \
      "$cmd_name${fn_args:+ ${fn_args:-}}" \
      "${fn_help:-NODESC}"
  done

}


# Auto generate help message
cli__help ()
{
  : "help=Show this help"

  local help_opts='' help_cmds=''
  help_opts=$(clish_usage_getopts app__init__getopts)
  help_cmds=$(clish_usage_cmd_prefix cli__)

  # Render output:
  cat <<EOF
${APP_NAME:-${0##*/}}: ${APP_DESC}

usage: ${0##*/} [<OPT>,..] <COMMAND> 
       ${0##*/} help

options:
$help_opts

commands:
$help_cmds

info:
  author: $APP_AUTHOR ${APP_EMAIL:+<$APP_EMAIL>}
  version: ${APP_VERSION:-0.0.1}-${APP_STATUS:-beta}${APP_DATE:+ ($APP_DATE)}
  license: ${APP_LICENSE:-MIT}
  ${APP_URL:+website: $APP_URL}
EOF
}

# Generate completion
cli__completion ()
{
  : "help=Show bash completion script"

  cat <<EOF
_${APP_NAME}_completions()
{
  if [ "\${#COMP_WORDS[@]}" != "2" ]; then
    return
  fi

  # keep the suggestions in a local variable
  local suggestions=(\$(compgen -W "$(clish_list_cmds|tr ':' ' ' )" -- "\${COMP_WORDS[1]}"))

  if [ "\${#suggestions[@]}" == "1" ]; then
    # if there's only one match, we remove the command literal
    # to proceed with the automatic completion of the number
    local number=\$(echo \${suggestions[0]/%\ */})
    COMPREPLY=("\$number")
  else
    # more than one suggestions resolved,
    # respond with the suggestions intact
    COMPREPLY=("\${suggestions[@]}")
  fi
}

complete -F _${APP_NAME}_completions ${APP_FILE}
EOF

}

# Show shellhook
cli__hook ()
{
  : "help=Show shell hook"
  : "args=[SHELL]"

  cat <<EOF
_${APP_NAME}_hook() {
  local previous_exit_status=$?;
  eval "\$($0 hook-env -s bash)";
  return \$previous_exit_status;
};
if [[ ";\${PROMPT_COMMAND:-};" != *";_${APP_NAME}_hook;"* ]]; then
  PROMPT_COMMAND="_${APP_NAME}_hook\${PROMPT_COMMAND:+;\$PROMPT_COMMAND}"
fi
EOF

  # echo "eval '${0}'"
  # _script_die 3 "Completion is not implemented"
}


# Extra libs
# =================

# Ask the user to confirm
clish_confirm () {
  local msg="Do you want to continue?"
  >&2 printf "%s" "${1:-$msg}"
  >&2 printf "%s" "([y]es or [N]o): "
  >&2 read -r REPLY
  case $(echo "$REPLY" | tr '[:upper:]' '[:lower:]') in
    y|yes) echo "true" ;;
    *)     echo "false" ;;
  esac
}


# Ask the user to input string
clish_input () {
  local msg="Please enter input:"
  local default=${2-}
  >&2 printf "%s" "${1:-$msg}${default:+ ($default)}: "
  >&2 read -r REPLY
  [[ -n "$REPLY" ]] || REPLY=${default}
  echo "$REPLY"
}


clish_yaml2json ()
{
  python3 -c 'import json, sys, yaml ; y = yaml.safe_load(sys.stdin.read()) ; print(json.dumps(y))'
}



# Helpers
# =================
alias _exec=_script_exec
alias _log=_script_log
alias _die=_script_die
alias _dump_vars=_script_debug_vars
alias _has_command=_script_has_command


# Core App
# =================



app__init ()
{
  # Useful shortcuts
  # shellcheck disable=SC2155
  export GIT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
  # shellcheck disable=SC2155
  export SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  # shellcheck disable=SC2155
  export WORK_DIR=${GIT_DIR:-${SCRIPT_DIR:-$PWD}}
  export PWD_DIR=${PWD}
}

app__init__getopts ()
{
  : "optargs=hnfv:m:"

  # local options=${*}
  local option=$1

  # echo "ARG=$ARGS"

  case "${OPTFLAG}" in
      h)
        : ",Show this help"
        cli__help; _script_die 0 ;;
      n)
        : ",Enable dry mode"
        _script_log INFO "Dry mode enabled"
        APP_DRY=true ;;
      f)
        : ",Enable force mode"
        _script_log INFO "Force mode enabled"
        APP_FORCE=true ;;
      v)
        : "DEBUG|INFO|WARN,Set verbosity"
        [[ ":$APP_LOG_SCALE:" == *":${OPTARG:-}:"* ]] || {
          _script_die 1 "Invalid option for -v: $OPTARG"
        }
        _script_log INFO "Log level set to: $OPTARG"
        APP_LOG_LEVEL=$OPTARG ;;
      m)
        : "TEXT,Set text message with spaces"
        _script_log INFO "Message set to: '$OPTARG'"
        # APP_MSG=$OPTARG 
        ;;
      *)
        
        if [[ "${option:0:2}" == "--" ]]; then
          _script_die 1 "Long option version are not supported: ${option}"
        else
          _script_die 1 "Unknown option: ${option}"
        fi
      ;;
  esac
}



# CLI Commands
# =================

cli__example ()
{
  : "meta=[ARG]"
  : "help=Example command"

  local arg="$*"
  echo "Called command: example $arg"

  _script_debug_args "$@"

  _script_fnmeta test_func

  IFS=$'\n' tmp=( $(_script_fnmeta test_func var3 meta2 var3) )
  set -- "${tmp[@]}"

  echo FINALLL TESSSTT
  _script_debug_args "$@"
  # echo "var3=1${1:-UNSET} meta2=${2:-UNSET}"


  echo "ICIIIII"
  # set -x
  _script_fnmeta test_func

}

test_func()
{
  : "meta=totot with espace"
  : "meta2=titi1 with espace"
  : "var3=titi2 with espasse"
}

# # Init main CLI only if not sourced
# (return 0 2>/dev/null) \
#   || clish_init "$@"

