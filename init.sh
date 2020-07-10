#!/bin/bash

$1 -s mitmproxy2har.py --mode reverse:$2 --anticache
