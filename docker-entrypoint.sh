#!/bin/sh

set -e

chown -R silero:silero .

if [ "$(id -u)" = "0" ]
then
    # restart script as user
    exec gosu silero "$@"
fi

exec "$@"