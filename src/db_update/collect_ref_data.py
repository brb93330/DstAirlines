#!/usr/bin/env python3

from update_db_with_countries import import_countries_from_lufthansa
from update_db_with_cities import import_cities_from_lufthansa
from update_db_with_airports import import_airports_from_wikipedia
from update_db_with_airlines import import_airlines_from_lufthansa
from update_db_with_aircraft import import_aircraft_from_lufthansa


def collect_ref_data():
    """
    Collect all reference data from the Lufthansa web-site and other sources and store them in the database
    """
    import_countries_from_lufthansa()
    import_cities_from_lufthansa()
    import_airports_from_wikipedia()
    import_aircraft_from_lufthansa()
    import_airlines_from_lufthansa()


if __name__ == '__main__':
    collect_ref_data()