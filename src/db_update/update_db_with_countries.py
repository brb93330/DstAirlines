import time

import airlines_db as db
import lufthansa_api_calls as lh


def import_countries_from_lufthansa():
    """
    Import all countries information from the Lufthansa web service
    into the airline's database.
    """

    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    # Create Lufthansa webservice
    luft_api = lh.LufthansaApi()

    offset = 0
    while True:
        response_dict = luft_api.get_ref_data_countries(offset=offset)
        if not response_dict or "CountryResource" not in response_dict:
            # No more result
            break

        # On itère sur le json d'éléments COUNTRY
        batch_size = 0
        countries = response_dict['CountryResource']['Countries']['Country']
        for country in countries:
            code = country.get('CountryCode')
            name = ""
            if 'Names' in country:
                names = country.get("Names")
                if 'Name' in names:
                    name = names.get("Name").get("$")
            batch_size += 1
            print(f"Country {offset + batch_size} : {code}: '{name}'")
            air_db.add_country(code, name)
        offset += batch_size
        # Pause half a second to avoid making too many calls per second
        print("Pause ...")
        time.sleep(0.5)

    air_db.close()
    print(f"Found {offset} countries")


if __name__ == '__main__':
    # Get all countries information from the Lufthansa website
    # and save them in the airlines database
    import_countries_from_lufthansa()

