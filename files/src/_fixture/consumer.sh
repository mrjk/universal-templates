#!/usr/bin/env bash
# fixture script with two snip anchors
set -euo pipefail

# >>> snip:id=fixture-a path=files/src/_fixture/snippet.sh ref=main
OLD_A=1
# <<< snip:id=fixture-a

# >>> snip:id=fixture-b path=files/src/_fixture/snippet.sh ref=main
OLD_B=1
# <<< snip:id=fixture-b

main() { :; }
main "$@"
