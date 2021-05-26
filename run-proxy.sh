#!/bin/bash

unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY

mitmdump --flow-detail 1 -s record.py --anticache -k
