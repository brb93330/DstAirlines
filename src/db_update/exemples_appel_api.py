import lufthansa_api_calls as lh


if __name__ == '__main__':
    client_id    =  "??????" # IDentifiant personnel à positionner ex: 983bp7d9ymap3gkzjcgbxrq28
    client_secret = "??????" # Secret personnel à positionner, ex QMxKVPnimM
    
    # Récupèration du token
    api_token = lh.get_api_token(client_id, client_secret)

    if len(api_token) == 0:
        print("Token non fourni")
        exit(0)

    luft_api = lh.LufthansaApi(api_token)

    # Liste des codes pays (pour l'exemple, on se limite aux 100 premiers)
    res = luft_api.get_ref_data_countries("DK", "fr", limit=100, offset=0)
    print("\nCountries :", res)

    res = luft_api.get_ref_data_cities("BER", "fr", limit=100, offset=0)
    print("\nCities :", res)

    res = luft_api.get_ref_data_airports("TXL", "fr", limit=100, offset=0)
    print("\nAirports :", res)

    res = luft_api.get_ref_data_nearest_airports(51.5, -0.142, "fr")
    print("\nNearest airports :", res)

    res = luft_api.get_ref_data_airlines("LH", 100, 0)
    print("\nAirlines :", res)

    res = luft_api.get_ref_data_aircraft("A58", 100, 0)
    print("\nAircraft :", res)

    res = luft_api.get_offers_seat_maps("LH401", "JFK", "FRA", "2023-03-02", "M")
    print("\nSeat Maps :", res)

    res = luft_api.get_offers_lounges("FRA", "", "", "fr")
    print("\nLounges :", res)

    res = luft_api.get_operations_flight_schedules("JFK", "FRA", "2023-03-02", "0", 100, 0)
    print("\nFlight schedules :", res)

    res = luft_api.get_operations_flight_status("LH401", "2023-03-02")
    print("\nFlight status :", res)

    res = luft_api.get_operations_flight_status_by_route("JFK", "FRA", "2023-03-02")
    print("\nFlight status by route :", res)

    res = luft_api.get_operations_flight_status_at_arrival_airport("FRA", "2023-03-03T08:00", "passenger", 100, 0)
    print("\nFlight status at arrival airport :", res)

    res = luft_api.get_operations_flight_status_at_departure_airport("JFK", "2023-03-02T15:00", "passenger", 100, 0)
    print("\nFlight status at departure airport :", res)

    res = luft_api.get_operations_customer_fight_information("LH401", "2023-03-02")
    print("\nCustomer flight information :", res)

    res = luft_api.get_operations_customer_fight_information_at_arrival_airport("FRA", "2023-03-03T08:00", 100, 0)
    print("\nCustomer flight information at arrival airport :", res)

    res = luft_api.get_operations_customer_fight_information_by_route("JFK", "FRA", "2023-03-02")
    print("\nCustomer flight information by route :", res)

    res = luft_api.get_operations_customer_fight_information_at_departure_airport("JFK", "2023-03-02T15:00")
    print("\nCustomer flight information at departure airport :", res)

    res = luft_api.get_flightschedules_passenger("LH", "", "02MAR23", "03MAR23", "1234567", "UTC", "JFK", "FRA")
    print("\nFlight schedule passenger :", res)
   
