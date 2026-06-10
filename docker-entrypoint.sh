#!/bin/sh

set -e

if [ "$(id -u)" = "0" ]
then
    chown -R silero:silero /app

    # restart script as silero user
    exec gosu silero "$@"
fi

exec "$@"