import requests
import json
from typing import Dict, Optional

import airlines_utils as utils

LH_BASE_URL = "https://api.lufthansa.com/"


def get_api_token(client_id, client_secret) -> str:
    """
    Collect a token to be authorized to call a Lufthansa web service
    Parameters:
        - client_id : account identifier to Lufthansa services
        - client_secret : secret key of account

    Return: 
        - token as a string
    """
    url = LH_BASE_URL + "v1/oauth/token"
    response = requests.post(url, data={"client_id": client_id,
                                        "client_secret": client_secret,
                                        "grant_type": "client_credentials"})
    if response.status_code == 200:
        ret_dict = json.loads(response.content.decode("utf-8"))
        return ret_dict["access_token"]
    
    return ""


class LufthansaApi:
    """
    Class to make all the calls to the Lufthansa website
    """

    def __init__(self, api_token: Optional[str] = None):
        self.__headers = None
        if not api_token:
            self.request_api_token()
        else:
            self.__api_token = api_token
        if not self.__api_token:
            raise KeyError("Missing LH token")

    def request_api_token(self):
        """
        Request the API token from the web service
        """
        # Make token to access Lufthansa webservice
        client_id, client_secret = utils.get_token_parameters()
        self.__api_token = get_api_token(client_id, client_secret)
        self.__headers = {"accept": "application/json", "Authorization": "bearer {}".format(self.__api_token)}

    def get_data_from_lufthansa(self, url_api: str) -> Dict:
        """
        Call the Lufthansa Api url and returns the result

        :param: url_api : full URL of the lufthansa Api

        :return: Dictionary json with service response, or empty dictionary
        """
        # Check we have a token
        if not self.__api_token:
            raise ValueError("Missing API token")

        response = requests.get(url_api, headers=self.__headers)
        return json.loads(response.content.decode("utf-8")) if response.status_code == 200 else {}

    def get_ref_data_countries(self, country_code: Optional[str] = None,
                               lang="fr", limit: int = 100, offset: int = 0) -> Dict:
        """
        Retrieves the complete details of one particular country or list of countries
        (and supports multiple languages wherever its applicable and available)

        Parameters:
            - country_code : 2-letter ISO 3166-1 country code, e.g. “DE”. Optional
            - lang : 2-letter ISO 639-1 language code, e.g. “EN”. Optional
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "CountriesStructureResponse"
        """
        if not country_code:
            country_code = ""
        url = LH_BASE_URL + f"v1/mds-references/countries/{country_code}?lang={lang}&limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_ref_data_cities(self, city_code: Optional[str] = None,
                            lang="fr", limit: int = 100, offset: int = 0) -> Dict:
        """
        Retrieves the complete details of one particular city or list of cities (and supports multiple
        languages wherever its applicable and available).

        Parameters:
            - city_code : 3-letter IATA city code. Optional
            - lang : 2-letter ISO 639-1 language code, e.g. “EN”. Optional
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger
             than 100 is given, 100 will be taken)
            - offset : Number of records skipped. Defaults to 0

        Return:
            - Dictionary json with "CountriesStructureResponse"
        """
        if not city_code:
            city_code = ""
        url = LH_BASE_URL + f"v1/mds-references/cities/{city_code}?lang={lang}&limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_ref_data_airports(self, iata_code, lang, limit=100, offset=0) -> Dict:
        """
        Retrieves the complete details of one particular airport or list of airports (and supports multiple
         languages wherever its applicable and available).

        Parameters:
            - iata_code : 3-letter IATA airport code, e.g. “TXL”. Optional
            - lang : 2-letter ISO 639-1 language code, e.g. “fr”. Optional
            - limit : Number of records returned per request. Maximum is 100
            (if a value bigger than 100 is given, 100 will be taken)
            - offset : Number of records skipped. Defaults to 0

        response:
            - Dictionary json with "AirportResourceStructureResponse"
        """
        url = LH_BASE_URL + "v1/mds-references/airports/"
        if iata_code:
            url = url + f"{iata_code}?lang={lang}&limit={limit}&offset={offset}&LHoperated=0"
        return self.get_data_from_lufthansa(url)

    def get_ref_data_nearest_airports(self, latitude, longitude, lang="fr") -> Dict:
        """
        Find the 5 closest airports to the given latitude and longitude, irrespective of the radius of
         the reference point.

        Parameters:
            - latitude
            - longitude
            - lang : 2-letter ISO 639-1 language code, e.g. “fr”. Optional

        Return:
            - Dictionary json with "AirportResourceStructureResponse"
        """
        url = LH_BASE_URL + f"v1/mds-references/airports/nearest/{latitude},{longitude}?lang={lang}"
        return self.get_data_from_lufthansa(url)

    def get_ref_data_airlines(self, airline_code=None, limit=100, offset=0) -> Dict:
        """
        Retrieves the complete details of one particular airline or list of airlines

        Parameters:
            - air_line_code : 2-character IATA airline/carrier code. Optional
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional
            -

        Return:
            - Dictionary json with "AirportResourceStructureResponse"
        """
        if not airline_code:
            airline_code = ""
        url = LH_BASE_URL + f"v1/mds-references/airlines/{airline_code}?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_ref_data_aircraft(self, aircraft_code: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict:
        """
        Retrieves the complete details of one particular aircraft or list of aircraft.

        Parameters:
            - aircraft_code : 3-character lufthansa aircraft code. Optional
            - limit : Number of records returned per request.
            Maximum is 100 (if a value bigger than 100 is given, 100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "AircraftResource"
        """
        if not aircraft_code:
            aircraft_code = ""
        url = LH_BASE_URL + f"v1/mds-references/aircraft/{aircraft_code}?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_offers_seat_maps(self, flight_number, origin, destination, date, cabin_class) -> Dict:
        """
        The seatmaps resource describes the layout of an aircraft's cabin. It provides characteristics of
        each seat and gives the location of other cabin items such as lavatories, gallies, stairs and exits.

        Parameters:
            - flight_number : Flight number including carrier code and any suffix (e.g. 'LH2037').
            - origin : Departure airport. 3-letter IATA airport code (e.g. 'TXL').
            - destination : Destination airport. 3-letter IATA airport code (e.g. 'MUC').
            - date : Departure date (YYYY-MM-DD).
            - cabinClass : Cabin class: 'M', 'E', 'C', 'F'. Some flights have fewer classes.

        Return:
            - Dictionary json with "SeatAvailabilityResourceStructureResponse"
        """
        url = LH_BASE_URL + f"v1/offers/seatmaps/{flight_number}/{origin}/{destination}/{date}/{cabin_class}"
        return self.get_data_from_lufthansa(url)

    def get_offers_lounges(self, iata_airport, cabin_class, tier_code, lang="fr") -> Dict:
        """
        The lounges resource returns information either for all available lounges or a specific lounge
        at a given airport or city, depending on the provided input parameters.
        The cabin_class and tier_code are exclusive, you can provide only one at the time.

        Parameters:
            - location : 3-letter IATA airport or city code (e.g. 'ZRH').
            - cabin_class : Cabin class: 'M', 'E', 'C', 'F'. Optional
            - tier_code : Frequent flyer level ('FTL', 'SGC', 'SEN', 'HON'). Optional
            - lang : 2-letter ISO 639-1 language code, e.g. “fr”. Optional

        Return:
            -  Dictionary json with "LoungesResourceStructureResponse"
        """
        url = LH_BASE_URL + f"v1/offers/lounges/{iata_airport}?"
        if cabin_class:
            url = url + f"cabinClass={cabin_class}&"
        elif tier_code:
            url = url + f"tierCode={tier_code}&"
        url = url + f"lang={lang}"
        return self.get_data_from_lufthansa(url)

    def get_operations_flight_schedules(self, origin, destination, from_date_time,
                                        direct_flights=0, limit=100, offset=0) -> Dict:
        """
        Retrieve a list of all possible flights (both direct and connecting) between two airports on a given
         date. Schedules are available for today and up to 360 days in the future.

        Parameters:
            - origin : Departure airport. 3-letter IATA airport code (e.g. 'ZRH').
            - destination : Destination airport. 3-letter IATA airport code (e.g. 'FRA').
            - from_date_time : Local departure date and optionally departure time (YYYY-MM-DD or YYYY-MM-DDTHH:mm).
             When not provided, time is assumed to be 00:01.
            - direct_flights : Show only direct flights (false=0, true=1). Default is false.
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightScheduleStructureResponse"
        """
        url = LH_BASE_URL + f"v1/operations/schedules/{origin}/{destination}/{from_date_time}?"\
                            f"directFlights={direct_flights}&limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_flight_status(self, flight_number, date) -> Dict:
        """
        Retrieve the status of a specific flight on a given date. The available date range is from 7 days
         in the past until 5 days in the future.

        Parameters:
            - flight_number : 2 letter IATA airline code + flight number.
            - date : Departure date in the local time of the departure airport. Supported range: yesterday until 5 days
             in the future. yyyy-MM-dd.

        Return:
            - Dictionary json with "FlightStatusResponseStructure"
        """
        url = LH_BASE_URL + f"v1/operations/flightstatus/{flight_number}/{date}"
        return self.get_data_from_lufthansa(url)

    def get_operations_flight_status_by_route(self, origin, destination, date, service_type="passenger") -> Dict:
        """
        Retrieve the status of flights between two airports on a given date. The available date range is
        from yesterday until 5 days in the future. At most the first 80 matching flights will be returned.
        It supports cargo or passenger or both flight types, by default it provides passenger flights only.

        :param: origin: 3 letter IATA airport code, e.g. “FRA”.
        :param: destination: 3 letter IATA airport code.
        :param: date: Departure date in the local time of the departure airport. Supported dates: yesterday until
         5 days in the future. yyyy-MM-dd.
        :param: service_type: ServiceType to retrieve cargo or passenger or both flights. default - passenger.
              enum: {all, passenger, cargo}. Optional

        :return: Dictionary json with "FlightStatusResponseStructure"
        """
        url = LH_BASE_URL + f"v1/operations/flightstatus/route/{origin}/{destination}/{date}?serviceType={service_type}"
        return self.get_data_from_lufthansa(url)

    def get_operations_flight_status_at_arrival_airport(self, airport_code, from_date_time, service_type,
                                                        limit=100, offset=0) -> Dict:
        """
        Retrieve the status of all flights arriving at a specific airport within a given time range which
         is set to 4 hours by default starting from time value quoted within fromDateTime input parameter.
                The permitted range for flights returned is from yesterday until 5 days in the future in 4 hours ranges.
                At most 80 flights will be returned.
                Various meta-links can be used to switch to previousRange 4 hours period or nextRange 4 hours period.
                It supports cargo or passenger or both flight types, by default it provides passenger flights only.

        Parameters:
            - airport_code : 3 letter IATA airport code, e.g. “FRA” .
            - from_date_time : Retrieve flights arriving after this time. yyyy-MM-ddTHH:mm.
            - service_type : enum: {all, passenger, cargo}. Optional
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
            100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightStatusResponseStructure"
        """
        url = LH_BASE_URL + f"v1/operations/flightstatus/arrivals/{airport_code}/{from_date_time}"\
                            f"?serviceType={service_type}&limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_flight_status_at_departure_airport(self, airport_code, from_date_time, service_type,
                                                          limit=100, offset=0) -> Dict:
        """
        Retrieve the status of all flights departing from a specific airport within a given time range.
        The permitted range is from yesterday until 5 days in the future. At most 80 flights will be returned.
        It supports cargo or passenger or both flight types, by default it provides passenger flights only.

        Parameters:
            - airport_code : 3 letter IATA airport code, e.g. “FRA”.
            - from_date_time : Retrieve flights departing after this time. yyyy-MM-ddTHH:mm.
            - service_type : enum: {all, passenger, cargo}. Optional
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightStatusResponseStructure"
        """
        url = LH_BASE_URL + f"v1/operations/flightstatus/departures/{airport_code}/{from_date_time}"\
                            f"?serviceType={service_type}&limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_customer_fight_information(self, flight_number, date, limit=100, offset=0) -> Dict:
        """
        Retrieve the status of a specific flight on a given date.

        Parameters:
            - flight_number : Flight number including carrier code and any suffix (e.g. 'LH400')
            - date : The departure date (YYYY-MM-DD) in the local time of the departure airport
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightInformationStructureResponse"
        """
        url = LH_BASE_URL + f"v1/operations/customerflightinformation/{flight_number}/{date}"\
                            f"?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_customer_fight_information_at_arrival_airport(self, airport_code, from_date_time,
                                                                     limit=100, offset=0) -> Dict:
        """
        Retrieve the status of all flights arriving at a specific airport within a given time range which is
         set to 4 hours by default starting from time value quoted within fromDateTime input parameter.
                The permitted range for flights returned is from yesterday until 5 days in the future in 4 hours ranges.
                At most 80 flights will be returned.
                Various meta-links can be used to switch to previousRange 4 hours period or nextRange 4 hours period.

        Parameters:
            - airport_code : 3-letter IATA airport code (e.g. 'ZRH').
            - from_date_time : Start of time range in local time of arrival airport (YYYY-MM-DDTHH:mm).
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightInformationStructureResponse"
        """
        url = LH_BASE_URL + f"v1/operations/customerflightinformation/arrivals/{airport_code}/{from_date_time}"\
                            f"?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_customer_fight_information_by_route(self, origin, destination, date,
                                                           limit=100, offset=0) -> Dict:
        """
        Retrieve the status of flights between two airports on a given date.

        Parameters:
            - origin : 3-letter IATA airport (e.g. 'FRA').
            - destination : 3-letter IATA airport code (e.g. 'JFK').
            - date : Departure date (YYYY-MM-DD) in local time of departure airport.
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightInformationStructureResponse"
        """
        url = LH_BASE_URL + f"v1/operations/customerflightinformation/route/{origin}/{destination}/{date}"\
                            f"?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_operations_customer_fight_information_at_departure_airport(self, airport_code, from_date_time,
                                                                       limit=100, offset=0) -> Dict:
        """
        Retrieve the status of all flights departing from a specific airport within a given time range.

        Parameters:
            - airport_code : Departure airport. 3-letter IATA airport code (e.g. 'HAM').
            - from_date_time : Start of time range in local time of departure airport (YYYY-MM-DDTHH:mm).
            - limit : Number of records returned per request. Maximum is 100 (if a value bigger than 100 is given,
             100 will be taken). Optional
            - offset : Number of records skipped. Defaults to 0. Optional

        Return:
            - Dictionary json with "FlightInformationStructureResponse"
        """
        url = LH_BASE_URL + f"v1/operations/customerflightinformation/departures/{airport_code}/{from_date_time}"\
                            f"?limit={limit}&offset={offset}"
        return self.get_data_from_lufthansa(url)

    def get_flight_schedules_passenger(self, airlines, start_date, end_date, days_of_operation,
                                       time_mode="UTC", origin="", destination="") -> Dict:
        """
        Returns passenger flights

        Parameters:
            - airlines : The list of airline codes ()
            - flightNumberRanges : The flight number range filter string. e.g.: '-100, 200, 100-200, 300-'
            - start_date : The period start date. SSIM date format DDMMMYY
            - end_date : The period end date. SSIM date format DDMMMYY
            - days_of_operation : The days of operation, i.e. the days of the week.
              Whitespace padded to 7 chars. E.g.: ' 34 6 '
            - time_mode : The time mode of the period of operations (ex: UTC)
            - origin : Search for flights departing from this station. 3 letter IATA airport code.
            - destination : Search for flights arriving at this station. 3 letter IATA airport code.

        Return:
            - Dictionary json with "passenger flights"
        """
        if not origin:
            origin = ""
        if not destination:
            destination = ""
        url = LH_BASE_URL + f"v1/flight-schedules/flightschedules/passenger?airlines={airlines}&startDate={start_date}"\
                            f"&endDate={end_date}&daysOfOperation={days_of_operation}&timeMode={time_mode}"
        if origin:
            url = url + f"&origin={origin}"
        if destination:
            url = url + f"&destination={destination}"
        return self.get_data_from_lufthansa(url)
