#!/bin/bash

while true; do
    curl https://sl.eu.ngrok.io/api/last_games > /tmp/last_games

    SERVER=$(cat /tmp/last_games | jq -r .[0].server_address)
    PORT=$(cat /tmp/last_games | jq -r .[0].server_port)
    DATE=$(cat /tmp/last_games | jq -r .[0].datetime)

    # Convert the ISO datetime to epoch seconds
    GAME_TIME=$(date -d "$DATE" +%s)
    CURRENT_TIME=$(date +%s)

    # Calculate difference in seconds
    TIME_DIFF=$((CURRENT_TIME - GAME_TIME))

    # 5 minutes = 300 seconds
    if [ $TIME_DIFF -gt 300 ]; then
        printf 'Game %s:%s from %s is %d seconds old (older than 5 minutes), skipping...\n' "$SERVER" "$PORT" "$DATE" "$TIME_DIFF"
    else
        printf 'Connecting to %s:%s (game from %s, %d seconds ago)...\n' "$SERVER" "$PORT" "$DATE" "$TIME_DIFF"
        powershell.exe -NoProfile -Command "Set-Location '\\\\wsl.localhost\\Ubuntu\\home\\simon\\uw-ai-yapper\\python'; python .\\main_observer.py $SERVER $PORT"
    fi

    sleep 10
done