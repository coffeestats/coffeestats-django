#!/bin/sh
# vim: sw=4 ts=4 et si ai

set -e

if [ -f .env ]; then
    exit 0
fi

generate_password() {
    dd if=/dev/urandom bs=64 count=1 2>/dev/null | base64 | tr -d '=+/[[:space:]]' | dd bs=32 count=1 2>/dev/null
}

cat > .env <<EOD
POSTGRES_PASSWORD=$(generate_password)
COFFEESTATS_SITE_ADMINMAIL=admin@coffeestats.org
COFFEESTATS_PGSQL_DATABASE=coffeestats
COFFEESTATS_PGSQL_HOSTNAME=db
COFFEESTATS_PGSQL_PORT=5432
COFFEESTATS_PGSQL_USER=coffeestats
COFFEESTATS_PGSQL_PASSWORD=$(generate_password)
COFFEESTATS_DOMAIN_NAME=coffeestats.org
COFFEESTATS_SITE_NAME=coffeestats.org
COFFEESTATS_SITE_SECRET=$(generate_password)
EOD
