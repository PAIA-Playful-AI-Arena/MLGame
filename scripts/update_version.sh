#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "You must enter exactly 1 command line argument for the version"
    exit 1
fi

echo "version = '$1'" > ./mlgame/version.py