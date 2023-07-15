import time
import airlines_db as db
import lufthansa_api_calls as lh


def import_aircraft_from_lufthansa():
    """
    Import all aircraft information from the Lufthansa web service
    into the airline's database.
    """

    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    # Create Lufthansa webservice
    luft_api = lh.LufthansaApi()

    offset = 0
    while True:  # Will stop when the service returns an empty result
        # Retrieve aircraft data from Lufthansa web service
        response_dict = luft_api.get_ref_data_aircraft(None, 200, offset)
        if not response_dict or "AircraftResource" not in response_dict:
            # No more result
            break

        # Loop over the batch of retrieved aircraft info
        batch_size = 0
        aircraft_summaries = response_dict.get("AircraftResource").get("AircraftSummaries").get("AircraftSummary")
        for aircraft_summary in aircraft_summaries:
            aircraft_code = aircraft_summary.get("AircraftCode")
            aircraft_name = ""
            if 'Names' in aircraft_summary:
                names = aircraft_summary.get("Names")
                if 'Name' in names:
                    aircraft_name = names.get("Name").get("$")
            airline_equip_code = aircraft_summary.get("AirlineEquipCode")
            batch_size += 1
            print(f"Aircraft {offset + batch_size} : {aircraft_code}: '{aircraft_name}' {airline_equip_code}")
            air_db.add_aircraft(aircraft_code, aircraft_name, airline_equip_code)
        offset += batch_size
        # Pause half a second to avoid making too many calls per second
        print("Pause ...")
        time.sleep(0.5)

    air_db.close()
    print(f"Found {offset} aircraft")


if __name__ == '__main__':
    # Get all aircraft information from the Lufthansa website
    # and save them in the airlines database
    import_aircraft_from_lufthansa()
