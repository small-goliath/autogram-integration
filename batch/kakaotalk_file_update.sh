#!/bin/bash

WATCH_FILE="/home/sch/autogram-integration/batch/kakaotalk/KakaoTalk_latest.txt"
cd /home/sch/autogram-integration
source .venv/bin/activate

inotifywait -m -e create,modify "${WATCH_FILE}" | while read FILE
do
    pip install -r requirements.txt
    echo "kakaotalk file update!!!"
    date
    python3 -m batch.kakaotalk_active
    python3 -m batch.kakaotalk_active_verify
done