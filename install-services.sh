#!/bin/bash
mkdir -p log

#docker image build -f dockerfiles/collect_ref_data.Dockerfile -t collect-ref-data:latest .

docker image build -f dockerfiles/analysis_api.Dockerfile -t lufthansa-analysis-api:latest .

# Run
# docker container run --volume $PWD/log:/log --name collect-data -d collect-ref-data:latest

docker container run -p 8000:8000 --name lufthansa-analysis -d lufthansa-analysis-api:latest
