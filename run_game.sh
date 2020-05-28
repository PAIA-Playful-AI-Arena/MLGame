#!/bin/bash
# The bash script for running the MLGame.py and catch the error when starts the game

# Run the command
message=$($@)

# If startup error is occurred, send the error
returncode=$?
if [[ $returncode == 1 ]]; then
    # Parse transition channel information
    for arg in "$@"
    do
        if [[ $arg == *"transition-channel"* ]]; then
            transition_channel=$arg
            break
        fi
    done

    # Pass the information to send_error.py
    python send_start_error.py $transition_channel "$message"
    exit $returncode
fi
