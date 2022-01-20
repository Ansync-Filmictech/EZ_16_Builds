#!/bin/bash

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Firmware Up-To-Date"
elif [ $LOCAL = $BASE ]; then
    echo "Firmware Out-Of-Date"
	git fetch --tags
	tag=$(git describe --tags `git rev-list --tags --max-count=1`)
	hexfile="../builds/${tag:4}.hex"
	./fw_update.py -f $hexfile
fi
