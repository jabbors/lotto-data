#!/bin/bash

echo "importing numbers and update stats"
docker run --rm -v ${PWD}/lotto.db:/importer/lotto.db lotto-importer python /importer/insert_and_update.py cron
