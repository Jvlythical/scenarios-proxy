#!/bin/bash

python3 hot_reload.py &

$1 -s record.py --anticache
