#!/bin/sh
# entrypoint.sh
# Starts Scrapyd in the background, waits for it to be ready,
# deploys the project egg, then schedules the spider.

set -e

echo ">>> Starting Scrapyd..."
scrapyd --pidfile= &
SCRAPYD_PID=$!

echo ">>> Waiting for Scrapyd to be ready..."
until curl -s http://localhost:6800/daemonstatus.json > /dev/null 2>&1; do
    sleep 1
done
echo ">>> Scrapyd is up."

echo ">>> Deploying project egg..."
cd /app/books_scraper
scrapyd-deploy local -p books_scraper

echo ">>> Scheduling spider..."
curl -s http://localhost:6800/schedule.json \
    -d project=books_scraper \
    -d spider=books

echo ">>> Spider scheduled. Keeping container alive..."
wait $SCRAPYD_PID
