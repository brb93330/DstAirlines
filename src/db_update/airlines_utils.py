from datetime import datetime, timedelta, date
import dateutil.parser
import os


def add_minutes_to_datetime(date_time, minutes=0):
    futur_date_time = datetime.fromtimestamp(datetime.strptime(date_time, "%d%b%y").timestamp())
    return futur_date_time + timedelta(minutes=minutes)


def convert_datetime_to_yyyymmdd_format(the_date):
    if the_date:
        return the_date.strftime('%Y%m%d')
    return ""


def convert_datetime_to_short_date_format(the_date):
    return the_date.strftime('%d%b%y').upper()


def get_list_formatted_dates(number_of_days):
    list_of_formatted_dates = [convert_datetime_to_short_date_format(date.today() + timedelta(1))]
    for i in range(0, number_of_days):
        list_of_formatted_dates.append(convert_datetime_to_short_date_format(date.today() - timedelta(i)))

    list_of_formatted_dates.reverse()
    return list_of_formatted_dates


def convert_string_date_to_datetime(your_date: str):
    if your_date:
        return dateutil.parser.parse(your_date)
    return None


def json_values_for_flight_status(res_json):
    DepartureAirportCode = ""
    DepartureScheduledTimeLocal = None
    DepartureScheduledTimeUTC = None
    DepartureActualTimeLocal = None
    DepartureActualTimeUTC = None
    DepartureTimeStatus = ""
    ArrivalAirportCode = ""
    ArrivalScheduledTimeLocal = None
    ArrivalScheduledTimeUTC = None
    ArrivalActualTimeLocal = None
    ArrivalActualTimeUTC = None
    ArrivalTimeStatus = ""
    MarketingCarrierAirlineID = ""
    MarketingCarrierFlightNumber = ""
    OperatingCarrierAirlineID = ""
    OperatingCarrierFlightNumber = ""
    EquipmentAircraftCode = ""
    AircraftRegistration = ""

    if res_json["FlightStatusResource"]["Flights"]["Flight"][0].get("Departure") is not None:
        DepartureAirportCode = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["AirportCode"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"].get("ScheduledTimeLocal") is not None:
            DepartureScheduledTimeLocal = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["ScheduledTimeLocal"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"].get("ScheduledTimeUTC") is not None:
            DepartureScheduledTimeUTC = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["ScheduledTimeUTC"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"].get("ActualTimeLocal") is not None:
            DepartureActualTimeLocal = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["ActualTimeLocal"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"].get("ActualTimeUTC") is not None:
            DepartureActualTimeUTC = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["ActualTimeUTC"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"].get("TimeStatus") is not None:
            DepartureTimeStatus = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["TimeStatus"]["Code"]
        ArrivalAirportCode = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["AirportCode"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"].get("ScheduledTimeLocal") is not None:
            ArrivalScheduledTimeLocal = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["ScheduledTimeLocal"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"].get("ScheduledTimeUTC") is not None:
            ArrivalScheduledTimeUTC = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["ScheduledTimeUTC"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"].get("ActualTimeLocal") is not None:
            ArrivalActualTimeLocal = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["ActualTimeLocal"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"].get("ActualTimeUTC") is not None:
            ArrivalActualTimeUTC = res_json["FlightStatusResource"]["Flights"]["Flight"][0].get("Arrival")["ActualTimeUTC"]["DateTime"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"].get("TimeStatus") is not None:
            ArrivalTimeStatus = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["TimeStatus"]["Code"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0].get("MarketingCarrier") is not None:
            MarketingCarrierAirlineID = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["MarketingCarrier"]["AirlineID"]
            MarketingCarrierFlightNumber = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["MarketingCarrier"]["FlightNumber"]
            OperatingCarrierAirlineID = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["MarketingCarrier"]["AirlineID"]
            OperatingCarrierFlightNumber = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["MarketingCarrier"]["FlightNumber"]
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0].get("Equipment") is not None:
            EquipmentAircraftCode = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Equipment"]["AircraftCode"]
            try:
                AircraftRegistration = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["Equipment"]["AircraftRegistration"]
            except Exception as e:
                AircraftRegistration=""
        if res_json["FlightStatusResource"]["Flights"]["Flight"][0].get("FlightStatus") is not None:
            FlightStatusCode = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["FlightStatus"]["Code"]
        ServiceType = res_json["FlightStatusResource"]["Flights"]["Flight"][0]["ServiceType"]

    return (DepartureAirportCode, DepartureScheduledTimeLocal, DepartureScheduledTimeUTC, DepartureActualTimeLocal,
            DepartureActualTimeUTC, DepartureTimeStatus, ArrivalAirportCode, ArrivalScheduledTimeLocal,
            ArrivalScheduledTimeUTC,
            ArrivalActualTimeLocal, ArrivalActualTimeUTC, ArrivalTimeStatus, MarketingCarrierAirlineID,
            MarketingCarrierFlightNumber,
            OperatingCarrierAirlineID, OperatingCarrierFlightNumber, EquipmentAircraftCode, AircraftRegistration,
            FlightStatusCode, ServiceType)


def get_token_parameters():
    key = os.getenv('LH_KEY')
    secret = os.getenv('LH_SECRET')
    if not key or not secret:
        raise ValueError('Missing LH key or secret in environment')
    return key, secret
