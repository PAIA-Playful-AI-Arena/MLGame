#!/bin/sh
# Exit the script if a command exits with a non-zero exit status
set -e

# Create a virtual frame buffer
Xvfb :1 -screen 0 1024x768x16 &> xvfb.log &
export DISPLAY=:1.0

# Execute the CMD
exec gosu appuser "$@"
