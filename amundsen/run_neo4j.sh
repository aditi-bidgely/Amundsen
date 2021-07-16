#!/bin/bash
docker-compose -f docker-amundsen.yml run -p7474:7474 -p7687:7687 neo4j
