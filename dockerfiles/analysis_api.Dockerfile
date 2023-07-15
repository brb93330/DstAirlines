FROM ubuntu:20.04
WORKDIR /src/dstairlines_api/
COPY /src/dstairlines_api/main.py .
COPY /src/dstairlines_api/utils.py .
COPY /src/dstairlines_api/requirements.txt .
COPY /src/dstairlines_api/.env .
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
EXPOSE 8000
CMD uvicorn main:api --host 0.0.0.0 --port 8000 --proxy-headers --reload
