#!/bin/bash
# snip: sync with: snip sync %FILE%
# snip: path=files/bin/ssh/id_gen.sh ref=main
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=main

#_IDENT="USER_HOST"
_IDENT=$(id -un)@$(hostname -f)

_DATE=$(date +'%Y%m%d')
_OUT="$(id -un)/.ssh/"
_OUT="$(getent passwd "${USER}" | cut -d: -f6)/.ssh/"

_IDENT2=${_IDENT2//@/_}

echo "Ident=$_IDENT, date=$_DATE out=$_OUT"
echo "Comment: ${_IDENT}:ALG_${_DATE}"
echo "Create keys in: ${_OUT}${_IDENT2}_ALG_${_DATE}"

ssh-keygen -t ed25519 -C "${_IDENT}:ed25519_${_DATE}" -f "${_OUT}${_IDENT2}_ed25519_${_DATE}"
ssh-keygen -t rsa -b 4096 -C "${_IDENT}:rsa4096_${_DATE}" -f "${_OUT}${_IDENT2}_rsa4096_${_DATE}"
ssh-keygen -t rsa -b 2048 -C "${_IDENT}:rsa2048_${_DATE}" -f "${_OUT}${_IDENT2}_rsa2048_${_DATE}"

echo "Done"


