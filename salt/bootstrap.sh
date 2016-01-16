#!/bin/sh -

# We just download the bootstrap script by default and execute that.
if [ -x /usr/bin/fetch ]; then
    /usr/bin/fetch -o - https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh | sh -s -- "$@"
elif [ -x /usr/bin/curl ]; then
    /usr/bin/curl -L https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh | sh -s -- "$@"
else
    python \
        -c 'import urllib; print urllib.urlopen("https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh").read()' \
        | sh -s -- "$@"
fi

cat >/etc/salt/minion <<EOF
file_client: local

file_roots:
  base:
    - /srv/salt/

pillar_roots:
  base:
    - /srv/pillar

log_file: file:///dev/log
EOF
