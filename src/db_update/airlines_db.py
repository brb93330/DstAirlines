import os

from dotenv import load_dotenv
from typing import Dict, Optional, Tuple

import mysql.connector
import airlines_utils as utils

# Load the environment variables, to get the database connection info
load_dotenv()


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
        'ssl_disabled': True,
        'auth_plugin': 'mysql_native_password'
    }
    return db_connection_config


class AirlinesDb:

    def __init__(self, db_config: Optional[Dict] = None):
        self.__db_config = db_config if db_config else get_database_connexion_config()
        self.__cnx = None

    def is_connected(self) -> bool:
        return self.__cnx is not None

    def connect(self):
        self.__cnx = mysql.connector.connect(**self.__db_config)
    
    def get_connexion(self):
        return self.__cnx
    
    def close(self):
        """
        Close the database connection
        """
        if self.__cnx:
            self.__cnx.close()
            self.__cnx = None
    
    def execute(self, sql_statement: str, data: Tuple):
        """
        Execute the given sql statement.

        :param: sql_statement: SQL statement
        :param: data: data for the query.
        """
        cursor = self.__cnx.cursor()
        try:
            cursor.execute(sql_statement, data)
        except Exception as e:
            print("SQL execute error :", e)
            pass
    
        # Make sure data is committed to the database
        self.__cnx.commit()
        cursor.close()

    def execute_select(self, sql_select_statement: str, data: Optional[Tuple]):
        """
        Execute the given select sql statement.

        :param: sql_select_statement: SELECT SQL statement
        :param: data: data for the query.
        """
        list_data = []
        cursor = self.__cnx.cursor()
        try:
            cursor.execute(sql_select_statement, data)
            list_data = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print("SQL SELECT execute error :", e)
            pass
    
        # Make sure data is committed to the database
        return list_data

    def add_country(self, code: str, name: str):
        """
        Add a country in the countries table.

        :param: code: the ISO 3166-1 alpha-2 country code
        :param: name: the country name
        """
        # SQL query to add a COUNTRY record in the 'COUNTRIES' table
        sql_add_country = "INSERT INTO DSTAIRLINES.COUNTRIES "\
                          "(COUNTRY_ID, COUNTRY_NAME) "\
                          "VALUES (%s, %s)"
        data = (code, name)
        self.execute(sql_add_country, data)

    def add_city(self, code: str, name: str, country_code: str):
        """
        Add a city in the cities table.

        :param: code: the ICAO alpha-3 city code
        :param: name: the city name
        :param: country_code: the ISO alpha-2 country code
        """
        # SQL query to add a CITY record in the 'CITIES' table
        sql_add_city = "INSERT INTO DSTAIRLINES.CITIES "\
                       "(CITY_ID, CITY_NAME, CITY_COUNTRY_FK) "\
                       "VALUES (%s, %s, %s)"
        data = (code, name, country_code)
        self.execute(sql_add_city, data)
       
    def add_airport(self, iata_code: str, icao_code: str, name: str, iata_city_code: str = None):
        """
        Add an airport in the airports table.

        :param: iata_code: airport IATA 3 letters code, e.g. "FRA" Frankfurt
        :param: icao_code: airport ICAO 4 letters code, e.g. "EDDF"
        :param: name: airport name, e.g. Frankfurt am Main Airport
        :param: iata_city_code: IATA code of the city of the airport, e.g. "FRA"
        """
        if iata_city_code:
            sql_add_airport = "INSERT INTO DSTAIRLINES.AIRPORTS " \
                              "(AIRPORT_ID, AIRPORT_ICAO, AIRPORT_NAME, CITY_ID_FK) " \
                              "VALUES (%s,%s,%s,%s)"
            data = (iata_code, icao_code, name, iata_city_code)
        else:
            sql_add_airport = "INSERT INTO DSTAIRLINES.AIRPORTS "\
                              "(AIRPORT_ID, AIRPORT_ICAO, AIRPORT_NAME) "\
                              "VALUES (%s,%s,%s)"
            data = (iata_code, icao_code, name)
        self.execute(sql_add_airport, data)

    def add_airline(self, iata_code: str, icao_code: str, name: str):
        """
        Add an airline in the airlines table.

        :param: iata_code: airline IATA 2 letters code, e.g. "LH"
        :param: icao_code: airline ICAO 3 letters code, e.g. "DLH"
        :param: name: airline name
        """
        sql_add_airline = "INSERT INTO DSTAIRLINES.AIRLINES "\
                          "(AIRLINE_ID, AIRLINE_ICAO, AIRLINE_NAME) "\
                          "VALUES (%s,%s,%s)"
        data = (iata_code, icao_code, name)
        self.execute(sql_add_airline, data)
    
    def add_aircraft(self, code: str, name: str, equip_code: str):
        """
        Add an aircraft in the aircraft table.

        :param: code: code internal to Lufthansa, e.g. 32B
        :param: name: complete name of this type of aircraft, e.g. Airbus A321 (sharklets)
        :param: equip_code: equipment code, e.g. A321
        """
        sql_add_aircraft = "INSERT INTO DSTAIRLINES.AIRCRAFT "\
                           "(AIRCRAFT_ID, AIRCRAFT_NAME, AIRCRAFT_AIRLINE_EQUIP_CODE) "\
                           "VALUES (%s,%s,%s)"
        data = (code, name, equip_code)
        self.execute(sql_add_aircraft, data)

    def last_sequence_flight_passenger(self):
        """
        Retrieval of the last sequence of the fight passenger rows

        """
        prepare_statement = "SELECT max(fsp_id) from FLIGHTS_SCHEDULES_PASSENGER "
        return self.execute_select(prepare_statement, None)

    def check_flight_passenger(self, airline, flight_number, start_date_utc, sequence_number, origin):
        """
        Check if the corresponding flight has been already saved in the database.

        :param: airline: Airline identifier
        :param: flight_number: flight number
        :param: startDateUTC: departure date of the flight
        :param: sequence_number: sequence number of the leg
        :param: origin: Departure airport
        """
        prepare_statement = '''
        select count(1) from DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER fsp 
        inner join DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER_LEGS fspl on fsp.fsp_id = fspl.fspl_id 
        where fsp.Fsp_airline_FK = %s and fsp_flight_number = %s and DATE_FORMAT(fsp.fsp_start_date_UTC, '%Y%m%d') = %s 
              and fspl.fspl_sequence_number = %s and fspl.FSPL_ORIGIN_AIRPORT_FK = %s
        '''
        data = (airline, flight_number, utils.add_minutes_to_datetime(start_date_utc, 0).strftime('%Y%m%d'),
                sequence_number, origin)
        return self.execute_select(prepare_statement, data)

    def check_flight_status(self, origin, start_date_utc, destination, flight_number, airline):
        """
        Check if the corresponding flight status has been already saved in the database.

        :param: origin: Departure airport
        :param: start_date_utc: departure date, in UTC, of the flight
        :param: destination: Arrival airport
        :param: flight_number: flight number
        :param: airline: Airline identifier
        """
        prepare_statement = '''
        select count(1) from DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ofs 
        where ofs.OFS_DEPARTURE_AIRPORT_FK = %s and DATE_FORMAT(ofs.OFS_DEPARTURE_SCHEDULED_TIME_LT,'%Y%m%d') = %s 
        and ofs.OFS_ARRIVAL_AIRPORT_FK = %s and ofs.OFS_OPERATING_CARRIER_FLIGHT_NUMBER = %s 
        and ofs.OFS_OPERATING_CARRIER_AIRLINE_FK = %s
        '''
        data = (origin, start_date_utc, destination, flight_number, airline)
        return self.execute_select(prepare_statement, data)
        
    def flight_status_key(self, origin, start_date_utc, destination, flight_number, airline):
        """
        Retrieval of the key data of a flight

        :param: origin: Departure airport
        :param: start_date_utc: departure date of the flight
        :param: destination: Arrival airport
        :param: flight_number: flight number
        :param: airline: Airline identifier
        """
        prepare_statement = '''
        select OFS_ID, OFS_DEPARTURE_FTS_FK, OFS_ARRIVAL_FTS_FK, OFS_FTS_FK 
        from DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ofs 
        where ofs.OFS_DEPARTURE_AIRPORT_FK = %s and DATE_FORMAT(ofs.OFS_DEPARTURE_SCHEDULED_TIME_LT,'%Y-%m-%d') = %s 
        and ofs.OFS_ARRIVAL_AIRPORT_FK = %s and ofs.OFS_OPERATING_CARRIER_FLIGHT_NUMBER = %s 
        and ofs.OFS_OPERATING_CARRIER_AIRLINE_FK = %s
        '''
        data = (origin, start_date_utc, destination, flight_number, airline)
        return self.execute_select(prepare_statement, data)
    

if __name__ == '__main__':
    # Try to get the environment parameters from the local protected storage
    default_db_config = get_database_connexion_config()
    print(default_db_config)
