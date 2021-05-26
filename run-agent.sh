#!/bin/bash

docker run -d -p 4200:4200 -v  $(pwd)/config/settings.yml:/app/config/settings.yml jvlythical/scenarios-agent:staging
