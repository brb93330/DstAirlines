import time

import airlines_db as db
import lufthansa_api_calls as lh


def import_cities_from_lufthansa():
    """
    Import all cities information from the Lufthansa web service
    into the airline's database.
    """

    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    # Create Lufthansa webservice
    luft_api = lh.LufthansaApi()

    offset = 0
    while True:  # Will stop when the service returns an empty result
        # Retrieve cities data from Lufthansa web service
        response_dict = luft_api.get_ref_data_cities(offset = offset)
        if not response_dict or "CityResource" not in response_dict:
            # No more result
            break

        batch_size = 0
        cities = response_dict['CityResource']['Cities']['City']
        for city in cities:
            code = city.get('CityCode')
            country_code = city.get('CountryCode')
            name = ""
            if 'Names' in city:
                names = city.get("Names")
                if 'Name' in names:
                    name = names.get("Name").get("$")
            batch_size += 1
            print(f"City {offset + batch_size} : {code}: '{name}'")
            air_db.add_city(code, name, country_code)
        offset += batch_size
        # Pause half a second to avoid making too many calls per second
        print("Pause ...")
        time.sleep(0.5)

    air_db.close()
    print(f"Found {offset} cities")


if __name__ == '__main__':
    # Get all cities information from the Lufthansa website
    # and save them in the airlines database
    import_cities_from_lufthansa()
