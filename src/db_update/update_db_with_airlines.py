import time

import airlines_db as db
import lufthansa_api_calls as lh


def import_airlines_from_lufthansa():
    """
    Import all airlines information from the Lufthansa web service
    into the airline's database.
    """

    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    # Create Lufthansa webservice
    luft_api = lh.LufthansaApi()

    offset = 0
    while True:  # Will stop when the service returns an empty result
        # Retrieve airline data from Lufthansa web service
        response_dict = luft_api.get_ref_data_airlines(None, 200, offset)
        if not response_dict or "AirlineResource" not in response_dict:
            # No more result
            break

        # Loop over the batch of retrieved airline info
        batch_size = 0
        airlines = response_dict.get("AirlineResource").get("Airlines").get("Airline")
        for airline in airlines:
            airline_id = airline.get("AirlineID")
            airline_icao = airline.get("AirlineID_ICAO")
            name = ""
            if 'Names' in airline:
                names = airline.get("Names")
                if 'Name' in names:
                    name = names.get("Name").get("$")
            batch_size += 1
            print(f"Airline {offset + batch_size} : {airline_id}: {airline_icao} '{name}'")
            air_db.add_airline(airline_id, airline_icao, name)
        offset += batch_size
        # Pause half a second to avoid making too many calls per second
        print("Pause ...")
        time.sleep(0.5)

    air_db.close()
    print(f"Found {offset} airlines")


if __name__ == '__main__':
    # Get all airlines information from the Lufthansa website
    # and save them in the airlines database
    import_airlines_from_lufthansa()
