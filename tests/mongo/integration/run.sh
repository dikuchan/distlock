#!/bin/env bash

function setup {
    docker container stop integration-distlock-mongo-1
    docker container rm integration-distlock-mongo-1
    docker compose up -d
    export DISTLOCK_MONGO_URL=mongodb://username:password@127.0.0.1:27017
}

function teardown {
    docker container stop integration-distlock-mongo-1
    docker container rm integration-distlock-mongo-1
    unset DISTLOCK_MONGO_URL
}

setup
poetry run pytest -s ..
teardown
