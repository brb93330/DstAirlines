FROM ubuntu:20.04
WORKDIR /src/dashboard/
COPY /src/dashboard/dstairline_dash.py .
COPY /src/dashboard/utils_dashboard.py .
COPY /src/dashboard/requirements.txt .
COPY /src/dashboard/.env .
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
EXPOSE 5000
CMD python3 dstairline_dash.py 
