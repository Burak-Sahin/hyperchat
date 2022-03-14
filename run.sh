#!/usr/bin/env sh

docker image pull redis:alpine
docker container run --name redis -p 6379:6379 -d redis:alpine


cd /hyperchat
# TODO: pass dynamic port from .env as part of container name for each chat server instance
docker image build -t buraksw/hyperchat -f Dockerfile . && docker container run -d buraksw/hyperchat
