#!/bin/bash

set -o pipefail
set -e

SCRIPT_DIR=`dirname "$0"`

# Initialize Database
python3 $SCRIPT_DIR/swarm initdb

# Launch vHPC Manager
python3 $SCRIPT_DIR/swarm webserver
