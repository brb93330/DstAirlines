from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import declarative_base
from typing import Dict
from datetime import datetime
import os



def get_database_connexion_config() -> Dict:
    """
    Get the database connection parameters from the environment
    """

    db_connection_config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'ssl_disabled': True
    }
    return db_connection_config

def get_api_users() -> Dict:
    """
    Retrieval of the users of the API
    """

    api_users = {
        "bruno": {
            "username": "bruno_dst_team",
            "name": "bruno",
            "password": os.getenv('API_PASSWORD_BRUNO')
        },

        "philippe" : {
            "username" :  "philippe_dst_team",
            "name" : "philippe",
            "password" : os.getenv('API_PASSWORD_PHILIPPE')
        },

        "tim" : {
            "username" :  "tim_dst_team",
            "name" : "tim",
            "password" : os.getenv('API_PASSWORD_TIMOTHEE')
        },

        "darshi" : {
            "username" :  "darshi_dst_team",
            "name" : "darshi",
            "password" : os.getenv('API_PASSWORD_DARSHI')
        }
    }
    return api_users

def string_to_date(theString):
    return datetime.strptime(theString, '%Y%m%d')
   

Base = declarative_base()

class AIRPORTS(Base):
    __tablename__ = "AIRPORTS"
    AIRPORT_ID = Column(String(10), primary_key=True)
    AIRPORT_ICAO = Column(String(10))
    AIRPORT_NAME = Column(String(100))
    CITY_ID_FK = Column(String(3))

    def __repr__(self):
        return "<User(name='%s', icao='%s')>" % (
            self.AIRPORT_NAME,
            self.AIRPORT_ICAO
        )

class OPERATIONS_FLIGHTS_STATUS(Base):
    __tablename__ = "OPERATIONS_FLIGHTS_STATUS"
    OFS_ID = Column(Integer, primary_key=True)
    OFS_DEPARTURE_AIRPORT_FK = Column(String(10))
    OFS_DEPARTURE_SCHEDULED_TIME_LT = Column(DateTime)
    OFS_DEPARTURE_SCHEDULED_TIME_UTC = Column(DateTime)
    OFS_DEPARTURE_ACTUAL_TIME_UTC = Column(DateTime)
    OFS_DEPARTURE_ACTUAL_TIME_LT = Column(DateTime)
    OFS_DEPARTURE_FTS_FK = Column(String(10))
    OFS_ARRIVAL_AIRPORT_FK = Column(String(10))
    OFS_ARRIVAL_SCHEDULED_TIME_UTC = Column(DateTime)
    OFS_ARRIVAL_SCHEDULED_TIME_LT = Column(DateTime)
    OFS_ARRIVAL_ACTUAL_TIME_LT = Column(DateTime)
    OFS_ARRIVAL_ACTUAL_TIME_UTC = Column(DateTime)
    OFS_ARRIVAL_FTS_FK = Column(String(10))
    OFS_MARKETING_CARRIER_AIRLINE_FK = Column(String(10))
    OFS_MARKETING_CARRIER_FLIGHT_NUMBER = Column(Integer)
    OFS_OPERATING_CARRIER_AIRLINE_FK = Column(String(10))
    OFS_OPERATING_CARRIER_FLIGHT_NUMBER = Column(Integer)
    OFS_AIRCRAFT_FK = Column(String(10))
    OFS_AIRCRAFT_REGISTRATION = Column(String(10))
    OFS_FTS_FK = Column(String(10))
    OFS_SERVICE_TYPE = Column(String(20))

 
class FLIGHTS_SCHEDULES_PASSENGER(Base):
    __tablename__ = "FLIGHTS_SCHEDULES_PASSENGER"
    FSP_ID = Column(Integer, primary_key=True)
    FSP_AIRLINE_FK = Column(String(10))
    FSP_FLIGHT_NUMBER = Column(String(10))
    FSP_DAYS_OF_OPERATIONS_UTC = Column(String(10))
    FSP_START_DATE_UTC = Column(Date)
    FSP_END_DATE_UTC = Column(Date)
    FSP_DAYS_OF_OPERATIONS_LT = Column(String(10))
    FSP_START_DATE_LT = Column(String(10))
    FSP_END_DATE_LT = Column(Date)


class FLIGHTS_SCHEDULES_PASSENGER_LEGS(Base):
    __tablename__ = "FLIGHTS_SCHEDULES_PASSENGER_LEGS"
    FSPL_ID = Column(Integer, primary_key=True)
    FSPL_SEQUENCE_NUMBER = Column(Integer)
    FSPL_ORIGIN_AIRPORT_FK = Column(String(10))
    FSPL_DESTINATION_AIRPORT_FK = Column(String(10))
    FSPL_SERVICE_TYPE = Column(String(10))
    FSPL_OWNER = Column(String(10))
    FSPL_TYPE = Column(String(10))
    FSPL_CONFIGURATION = Column(String(20))
    FSPL_DEPARTURE_TIME_UTC = Column(Date)
    FSPL_DEPARTURE_TIME_LT = Column(Date)
    FSPL_DEPARTURE_DIFF_TIME_UTC = Column(Integer)
    FSPL_DEPARTURE_DIFF_TIME_LT = Column(Integer)
    FSPL_ARRIVAL_TIME_UTC = Column(Date)
    FSPL_ARRIVAL_TIME_LT = Column(Date)
    FSPL_ARRIVAL_DIFF_TIME_UTC = Column(Integer)
    FSPL_ARRIVAL_DIFF_TIME_LT = Column(Integer)


class AIRCRAFT(Base):
    __tablename__ = "AIRCRAFT"
    AIRCRAFT_ID= Column(Integer, primary_key=True)
    AIRCRAFT_NAME  = Column(String(100))
    AIRCRAFT_AIRLINE_EQUIP_CODE = Column(String(10))


class COUNTRIES(Base):
    __tablename__ = "COUNTRIES"
    COUNTRY_ID = Column(String(10), primary_key=True)
    COUNTRY_NAME = Column(String(100))


class CITIES(Base):
    __tablename__ = "CITIES"
    CITY_ID = Column(String(10), primary_key=True)
    CITY_NAME = Column(String(100))
    CITY_COUNTRY_FK = Column(String(10))


class AIRLINES(Base):
    __tablename__ = "AIRLINES"
    AIRLINE_ID = Column(String(10), primary_key=True)
    AIRLINE_ICAO = Column(String(10))
    AIRLINE_NAME = Column(String(100))


class FLIGHT_TIME_STATUS(Base):
    __tablename__ = "FLIGHT_TIME_STATUS"
    FTS_ID = Column(String(10), primary_key=True)
    FTS_DEFINITION = Column(String(50))


