title () 
{
  local msg="$@"
  echo 
  echo "========================"
  echo "  $msg"
  echo "========================"
}

log ()
{
  >&2 echo "$@"
}

pydict2json ()
{
  python3 -c "import sys, json, ast; print(json.dumps(ast.literal_eval(sys.stdin.read().strip())))"
}
