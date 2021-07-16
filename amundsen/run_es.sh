#!/bin/bash
docker-compose -f docker-amundsen.yml run -p9200:9200 -p9300:9300 elasticsearch
