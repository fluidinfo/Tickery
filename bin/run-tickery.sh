#!/bin/sh

# This is a script that can start Tickery. It expects several secret
# password/key values to be set in the environment (see below).

test -d /srv/tickery || {
  cat 2>&1 <<EOF

This script is designed to run only on tickery.net (which has a /srv/tickery
directory - that you don't have). To start Tickery locally, just go to the
top level of your tree, and use:

  $ make
  $ make run
EOF
  exit 1
}

test -n "$TICKERY_CONSUMER_KEY" || {
  echo 'You need to set TICKERY_CONSUMER_KEY in your environment.' 2>&1
  exit 2
}

test -n "$TICKERY_CONSUMER_SECRET" || {
  echo 'You need to set TICKERY_CONSUMER_SECRET in your environment.' 2>&1
  exit 3
}

test -n "$FLUIDINFO_TWITTER_PASSWORD" || {
  echo 'You need to set FLUIDINFO_TWITTER_PASSWORD in your environment.' 2>&1
  exit 4
}

VIRTUALENV_HOME=/srv/tickery/current
TICKERY_USER=tickery

exec /sbin/start-stop-daemon --start --chdir $VIRTUALENV_HOME \
    --chuid $TICKERY_USER --exec $VIRTUALENV_HOME/bin/twistd -- \
    --pidfile=/srv/tickery/current/var/run/tickery.pid \
    --logfile=/srv/tickery/current/var/log/tickery.log tickery \
    --cache /srv/tickery/CACHE
