export DJANGO_SETTINGS_MODULE=coffeestats.settings.local
export COFFEESTATS_MAIL_FROM_ADDRESS={{ pillar['general']['mailfrom'] }}
export COFFEESTATS_PGSQL_DATABASE={{ pillar['database']['database'] }}
export COFFEESTATS_PGSQL_HOSTNAME=localhost
export COFFEESTATS_PGSQL_PASSWORD={{ pillar['database']['password'] }}
export COFFEESTATS_PGSQL_PORT={{ pillar['database']['port'] }}
export COFFEESTATS_PGSQL_USER={{ pillar['database']['user'] }}
export COFFEESTATS_PIWIK_HOST={{ salt['pillar.get']('piwik:host', 'piwik.localhost') }}
export COFFEESTATS_PIWIK_SITEID={{ salt['pillar.get']('piwik:siteid', '1') }}
export COFFEESTATS_SITE_ADMINMAIL={{ pillar['general']['adminemail'] }}
export COFFEESTATS_SITE_NAME="{{ pillar['general']['sitename'] }}"
export COFFEESTATS_SITE_SECRET={{ pillar['general']['sitesecret'] }}
export COFFEESTATS_DOMAIN_NAME={{ pillar['general']['domainname'] }}
