#!/bin/sh

export COMPOSE_FILE="test/docker-compose.yaml"

docker-compose down \
&& docker-compose build \
&& docker-compose run test
