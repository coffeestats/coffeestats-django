#!/bin/sh

set -e

if [ $# -lt 5 ]; then
    echo "Usage: $0 <mysqldump.gz> <mysqlhost> <mysqluser> <mysqlpass> <mysqldb>"
    exit 1
fi

DUMPFILE=$1
MYSQLHOST=$2
MYSQLUSER=$3
MYSQLPASS=$4
MYSQLDB=$5

mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -p"$MYSQLPASS" -e "DROP DATABASE IF EXISTS $MYSQLDB; CREATE DATABASE IF NOT EXISTS $MYSQLDB CHARACTER SET 'LATIN1';"
zcat "$DUMPFILE" | mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -p"$MYSQLPASS" "$MYSQLDB"

mysql -u "$MYSQLUSER" -h "$MYSQLHOST" -p"$MYSQLPASS" "$MYSQLDB" <<EOD
\W
UPDATE cs_users SET utimezone='' WHERE utimezone IS NULL;

DELETE FROM cs_caffeine
WHERE NOT EXISTS (SELECT * FROM cs_users WHERE uid=cuid);
UPDATE cs_caffeine SET cdate=centrytime WHERE cdate < '2012-01-01';
UPDATE cs_caffeine SET ctimezone='' WHERE ctimezone IS NULL;
EOD

psql -U "$COFFEESTATS_PGSQL_USER" -h "$COFFEESTATS_PGSQL_HOSTNAME" -w "$COFFEESTATS_PGSQL_DATABASE" << EOD
DROP TABLE IF EXISTS cs_users, cs_caffeine;

CREATE TABLE cs_users (
  uid integer primary key,
  ulogin varchar(30) not null unique,
  uemail varchar(128) not null unique,
  ufname varchar(128) not null,
  uname varchar(128) not null,
  ucryptsum varchar(60) not null,
  ujoined timestamp not null,
  ulocation varchar(128) not null,
  upublic smallint not null default 1,
  utoken varchar(32) not null unique,
  uactive smallint not null,
  utimezone varchar(40) not null
);

CREATE TABLE cs_caffeine (
  cid integer primary key,
  ctype smallint not null,
  cuid integer not null references cs_users(uid),
  cdate timestamp not null,
  centrytime timestamp not null,
  ctimezone varchar(40) not null
);
EOD

mysqldump -u "$MYSQLUSER" -h "$MYSQLHOST" -p"$MYSQLPASS" -c -n -t \
--compatible=postgresql "$MYSQLDB" cs_users cs_caffeine | \
egrep -v '(UN|)LOCK TABLES' | \
iconv -f "ISO-8859-1" -t "UTF-8" | \
psql -U "$COFFEESTATS_PGSQL_USER" -h "$COFFEESTATS_PGSQL_HOSTNAME" -w "$COFFEESTATS_PGSQL_DATABASE"

psql -U "$COFFEESTATS_PGSQL_USER" -h "$COFFEESTATS_PGSQL_HOSTNAME" -w "$COFFEESTATS_PGSQL_DATABASE" << EOD
BEGIN;
INSERT INTO caffeine_user
    (id, username, email, first_name, last_name, cryptsum, date_joined,
     location, public, token, is_active, timezone, password, last_login,
     is_superuser, is_staff)
SELECT uid, ulogin, uemail, ufname, uname, ucryptsum, ujoined, ulocation,
     upublic = 1, utoken, uactive = 1, utimezone, '', CURRENT_TIMESTAMP,
     'false', 'false'
FROM cs_users;
UPDATE caffeine_user SET is_superuser='true', is_staff='true'
WHERE username IN ('jandd', 'noqqe');

INSERT INTO caffeine_caffeine (id, ctype, user_id, date, entrytime, timezone)
SELECT cid, ctype, cuid, cdate, centrytime, ctimezone FROM cs_caffeine;

SELECT setval('caffeine_caffeine_id_seq'::regclass, MAX(id)) FROM caffeine_caffeine;
SELECT setval('caffeine_user_id_seq'::regclass, MAX(id)) FROM caffeine_user;

DROP TABLE cs_caffeine;
DROP TABLE cs_users;
COMMIT;
EOD
