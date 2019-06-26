#!/usr/bin/env bash

# If moving deenis in an existing $PATH away from the Python directory, set $DEENIS_PATH to the
# Python directory.
DEENIS_PATH="./deenis"

if [[ $# -eq 0 ]] ; then
  # If no argument, append --help
  python3 $DEENIS_PATH/cli.py --help
else
  # Send all arguments
  python3 $DEENIS_PATH/cli.py $@
  exit 0
fi
