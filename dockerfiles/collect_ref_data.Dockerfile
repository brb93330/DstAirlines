FROM ubuntu:20.04
ENV SRC=/src
WORKDIR $SRC
COPY src/db_update/airlines_db.py src/db_update/airlines_utils.py src/db_update/lufthansa_api_calls.py src/db_update/collect_ref_data.py .
COPY src/db_update/update_db_with_countries.py src/db_update/update_db_with_cities.py src/db_update/update_db_with_airports.py .
COPY src/db_update/update_db_with_airlines.py src/db_update/update_db_with_aircraft.py .
COPY src/db_update/requirements.txt .env .
RUN apt-get update && apt-get install python3-pip -y && pip3 install -r requirements.txt
RUN ls -al
WORKDIR /log
CMD python3 $SRC/collect_ref_data.py
