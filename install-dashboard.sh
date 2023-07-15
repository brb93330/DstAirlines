#!/bin/bash
mkdir -p log

#docker image build -f dockerfiles/collect_ref_data.Dockerfile -t collect-ref-data:latest .

docker image build -f dockerfiles/dashboard.Dockerfile -t dashboard-dstairlines:1.0.0 .

# Run
# docker container run --volume $PWD/log:/log --name collect-data -d collect-ref-data:latest

docker container run -p 5000:5000 --name dashboard-dstairlines -d dashboard-dstairlines:1.0.0
