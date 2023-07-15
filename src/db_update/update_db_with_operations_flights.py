import airlines_utils as u
import lufthansa_api_calls as lh
import airlines_utils as utils
import json
import airlines_db as db
from datetime import datetime

def insert_or_update_data_in_operations_flight_status_table_from_ws():
    
    """""
    Fonction : Insertion des données de statuts des vols  à partir du service Operations Flight Status de l'API Lufthansa
    
    Parameters:

    Return: 
        - Pas de retour (au pire une erreur survient mais on ne va pas remettre en question toutes les insertions faites à cause d'une erreur...
    """

    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    
    # Create Lufthansa webservice
    luft_api = None
    try:
        luft_api = lh.LufthansaApi()
    except Exception as e:
        print("Pas de token")
        raise ValueError('Missing LH key or secret in environment')

    # Récupération des vols planifiés stockés en base (le service des statuts ne récupère que les 7 derniers jours mais pour des raisons de contraintes du nbre d'appels on ne récupère que les 2 derniers jours)
    prepareStatement_fsp   = "select fsp.FSP_AIRLINE_FK , fsp.FSP_FLIGHT_NUMBER , DATE_FORMAT(fsp.fsp_start_date_LT, '%Y-%m-%d') from DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER fsp "
    prepareStatement_fsp  += "inner join DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER_LEGS fspl on fsp.fsp_id = fspl.fspl_id "
    prepareStatement_fsp  += "where DATE_FORMAT(fsp.fsp_start_date_UTC, '%Y%m%d') >=  DATE_FORMAT(ADDDATE(SYSDATE(), -1), '%Y%m%d') "
    prepareStatement_fsp  += "and (fspl.FSPL_ORIGIN_AIRPORT_FK , fspl.FSPL_DESTINATION_AIRPORT_FK, fspl.FSPL_DEPARTURE_TIME_UTC,fsp.FSP_AIRLINE_FK,fsp.FSP_FLIGHT_NUMBER) not in "
    prepareStatement_fsp  += "(select ofs.OFS_DEPARTURE_AIRPORT_FK , ofs.OFS_ARRIVAL_AIRPORT_FK, ofs.OFS_DEPARTURE_SCHEDULED_TIME_UTC, ofs.OFS_OPERATING_CARRIER_AIRLINE_FK, ofs.OFS_OPERATING_CARRIER_FLIGHT_NUMBER "
    prepareStatement_fsp  += "from DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ofs where ofs.OFS_FTS_FK = 'LD') "
    prepareStatement_fsp  += "order by fsp.FSP_AIRLINE_FK asc , fsp.FSP_FLIGHT_NUMBER asc"

    listData = air_db.execute_select(prepareStatement_fsp, None)

    i=0
    # Prise en contraintes d'appels (1000 appels par heure max)
    #time1 = datetime.now()
    
    # Récupération de tous les vols (en V1, uniquement LH)
    print ("Debut MAJ Statut pour ", len(listData))
    for (airline, flightNumber, startDate ) in listData:
        i += 1 

        res = luft_api.get_operations_flight_status(airline + flightNumber, startDate)

        json_result = json.dumps(res)

        resJson = json.loads(json_result)

        # On passe au suivant si on n'a aucun résultat...    
        if len(resJson) == 0:
            #print(" -- Suivant -- ")
            continue

        if i>1000:
            break

        try:
            DepartureAirportCode = None
            DepartureScheduledTimeLocal = None
            DepartureScheduledTimeUTC = None
            DepartureActualTimeLocal = None
            DepartureActualTimeUTC = None
            DepartureTimeStatus = None
            ArrivalAirportCode = None
            ArrivalScheduledTimeLocal = None
            ArrivalScheduledTimeUTC = None
            ArrivalActualTimeLocal = None
            ArrivalActualTimeUTC = None
            ArrivalTimeStatus = None
            MarketingCarrierAirlineID = None
            MarketingCarrierFlightNumber = None
            OperatingCarrierAirlineID = None
            OperatingCarrierFlightNumber = None
            EquipmentAircraftCode = None
            EquipmentAircraftRegistration = None
            FlightStatusCode  = None
            ServiceType = None

            # Parcours de chaque vol
            (DepartureAirportCode,DepartureScheduledTimeLocal,DepartureScheduledTimeUTC,DepartureActualTimeLocal,
            DepartureActualTimeUTC,DepartureTimeStatus,ArrivalAirportCode,ArrivalScheduledTimeLocal,ArrivalScheduledTimeUTC,
            ArrivalActualTimeLocal,ArrivalActualTimeUTC,ArrivalTimeStatus,MarketingCarrierAirlineID,MarketingCarrierFlightNumber,
            OperatingCarrierAirlineID,OperatingCarrierFlightNumber,EquipmentAircraftCode, EquipmentAircraftRegistration,FlightStatusCode, ServiceType) = utils.json_values_for_flight_status(resJson)
        
            # Si le statut n'existe pas : Insertion, sinon mis à jour
            if not air_db.check_flight_status(DepartureAirportCode, utils.convert_datetime_to_yyyymmdd_format(utils.convert_string_date_to_datetime(startDate)), ArrivalAirportCode, OperatingCarrierFlightNumber, OperatingCarrierAirlineID)[0][0] > 0:
               # print("Not  : ", OperatingCarrierFlightNumber, " -- ", DepartureAirportCode, " -- " , DepartureScheduledTimeUTC , " -- ", OperatingCarrierAirlineID  ," -- ", FlightStatusCode)
               # Insertion du statut du vol dans la table OPERATIONS_FLIGHTS_STATUS
                prepareStatement  = "Insert into DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ("
                prepareStatement += "OFS_DEPARTURE_AIRPORT_FK, OFS_DEPARTURE_SCHEDULED_TIME_LT, OFS_DEPARTURE_SCHEDULED_TIME_UTC, OFS_DEPARTURE_ACTUAL_TIME_LT, "
                prepareStatement += "OFS_DEPARTURE_ACTUAL_TIME_UTC, OFS_DEPARTURE_FTS_FK, OFS_ARRIVAL_AIRPORT_FK, "
                prepareStatement += "OFS_ARRIVAL_SCHEDULED_TIME_UTC, OFS_ARRIVAL_SCHEDULED_TIME_LT, OFS_ARRIVAL_ACTUAL_TIME_LT, OFS_ARRIVAL_ACTUAL_TIME_UTC, "
                prepareStatement += "OFS_ARRIVAL_FTS_FK, OFS_MARKETING_CARRIER_AIRLINE_FK, OFS_MARKETING_CARRIER_FLIGHT_NUMBER, OFS_OPERATING_CARRIER_AIRLINE_FK, "
                prepareStatement += "OFS_OPERATING_CARRIER_FLIGHT_NUMBER, OFS_AIRCRAFT_FK, OFS_AIRCRAFT_REGISTRATION, OFS_FTS_FK, OFS_SERVICE_TYPE) "
                prepareStatement += " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                fsplData = (DepartureAirportCode, utils.convert_string_date_to_datetime(DepartureScheduledTimeLocal), utils.convert_string_date_to_datetime(DepartureScheduledTimeUTC),
                            utils.convert_string_date_to_datetime(DepartureActualTimeLocal), utils.convert_string_date_to_datetime(DepartureActualTimeUTC),
                            DepartureTimeStatus, ArrivalAirportCode, utils.convert_string_date_to_datetime(ArrivalScheduledTimeUTC), utils.convert_string_date_to_datetime(ArrivalScheduledTimeLocal),
                            utils.convert_string_date_to_datetime(ArrivalActualTimeLocal), utils.convert_string_date_to_datetime(ArrivalActualTimeUTC),
                            ArrivalTimeStatus, MarketingCarrierAirlineID, MarketingCarrierFlightNumber,
                            OperatingCarrierAirlineID, OperatingCarrierFlightNumber, EquipmentAircraftCode, EquipmentAircraftRegistration, FlightStatusCode, ServiceType
                        )
                
                air_db.execute(prepareStatement, fsplData)
            else:
                #print("Else  : ", OperatingCarrierFlightNumber, " -- ", DepartureAirportCode, " -- " , DepartureScheduledTimeUTC , " -- ", OperatingCarrierAirlineID  ," -- ", FlightStatusCode)
                
                # Récupération de la clé de la ligne et des statuts à mettre à jour
                flightStatusKey, departure_status, arrival_status, flight_status = air_db.flight_status_key(DepartureAirportCode, startDate, ArrivalAirportCode, flightNumber, airline)[0]
                
                # On met à jour si au moins l'un des statuts a été modifié. On met aussi les "vraies" dates (les "ACTUAL") à jour.
                if flightStatusKey!= None and (departure_status != DepartureTimeStatus or arrival_status != ArrivalTimeStatus or flight_status != FlightStatusCode):
                    #print("flightStatusKey  : ", OperatingCarrierFlightNumber, " -- ", DepartureAirportCode, " -- " , DepartureScheduledTimeUTC , " -- ", OperatingCarrierAirlineID  ," -- ", FlightStatusCode, " -- ", ArrivalAirportCode)
                    prepareStatement  = "update DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS set "
                    prepareStatement += "OFS_DEPARTURE_FTS_FK=%s,"
                    prepareStatement += "OFS_ARRIVAL_FTS_FK=%s,"
                    prepareStatement += "OFS_FTS_FK=%s, "
                    prepareStatement += "OFS_DEPARTURE_ACTUAL_TIME_UTC=%s, "
                    prepareStatement += "OFS_DEPARTURE_ACTUAL_TIME_LT=%s,"
                    prepareStatement += "OFS_ARRIVAL_ACTUAL_TIME_UTC=%s,"
                    prepareStatement += "OFS_ARRIVAL_ACTUAL_TIME_LT=%s "
                    prepareStatement += "where OFS_ID=%s"
                    
                    fsplData = (DepartureTimeStatus, ArrivalTimeStatus, FlightStatusCode,
                                utils.convert_string_date_to_datetime(DepartureActualTimeUTC),
                                utils.convert_string_date_to_datetime(DepartureActualTimeLocal),
                                utils.convert_string_date_to_datetime(ArrivalActualTimeUTC),
                                utils.convert_string_date_to_datetime(ArrivalActualTimeLocal),
                                flightStatusKey)
                    
                    air_db.execute(prepareStatement, fsplData)
            
        except Exception as e:
            print(e)
            print("Erreur : ", OperatingCarrierFlightNumber, " -- ", DepartureAirportCode, " -- " , DepartureScheduledTimeUTC , " -- ", OperatingCarrierAirlineID  ," -- ", FlightStatusCode)
            continue


if __name__ == '__main__':
    try:
        print("Debut mise à jour : ", str(datetime.now()))
        insert_or_update_data_in_operations_flight_status_table_from_ws ()
        print("Fin mise à jour : ", str(datetime.now()))
    except Exception as e:
        print("Erreur Gobale")
        print(e)

