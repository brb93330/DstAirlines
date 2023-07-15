from datetime import datetime

import airlines_utils as u
import lufthansa_api_calls as lh
import airlines_utils as utils
import airlines_db as db


def insert_data_in_flights_schedules_tables_from_ws(airlines, start_date, end_date, days_of_operation,
                                                    time_mode="UTC", origin="", destination=""):
    
    """""
    Fonction : Insertion des données des vols planifiés à partir du service Flight Schedules de l'API Lufthansa
    
    Parameters:
        - airlines : Ligne concernée. Obligatoire. Pour la V1, il s'agira de LH
        - start_date : Jour de départ en UTC du vol (format 01MAR23)
        - end_date : Jour d'arrivée en UTC du vol (format 01MAR23)
        - days_of_operation : Les jours de la demaine concernés. Ici en V1  tous les jours (1234567)
        - timeMode : Heure "UTC" ou LT. Choixc fait du UTC
        - origin : Aéoroport de départ. Ici one ne le positionne pas car on veut tous les vols
        - destination : Aéoroport d'arrivée. Ici one ne le positionne pas car on veut tous les vols

    Return: 
        - Pas de retour (au pire une erreur survient mais on ne va pas remettre en question toutes les insertions faites à cause d'une erreur...
    """
    # Connect to the default airlines database
    air_db = db.AirlinesDb()
    air_db.connect()
    cnx = air_db.get_connexion() 

    # Create Lufthansa webservice
    luft_api = lh.LufthansaApi()

    # Récupération de tous les vols (en V1, uniquement LHJ, par d'aéoroports)
    resJson = luft_api.get_flight_schedules_passenger(airlines, start_date, end_date, days_of_operation,
                                                      time_mode, origin, destination)
    # On sort de la fonction si on n'a aucun résultat...
    #if resJson == '':
    #    exit

    # Parcours de chaque vol
    for flightSchedule in resJson:
        theLegs = flightSchedule.get("legs")

        # Dans la V1, on ne prend que les vols sans escale, soit 1 seul "legs"
        if len(theLegs)>1:
            continue
        
        theFirstLeg = theLegs[0]

        airLine                          = flightSchedule.get("airline")
        flightNumber                     = flightSchedule.get("flightNumber")
        startDateUTC                     = flightSchedule.get("periodOfOperationUTC").get("startDate")
        endDateUTC                       = flightSchedule.get("periodOfOperationUTC").get("endDate")
        daysOfOperationUTC               = flightSchedule.get("periodOfOperationUTC").get("daysOfOperation")
        startDateLT                      = flightSchedule.get("periodOfOperationLT").get("startDate")
        endDateLT                        = flightSchedule.get("periodOfOperationLT").get("endDate")
        daysOfOperationLT                = flightSchedule.get("periodOfOperationLT").get("daysOfOperation")
        sequenceNumber                   = theFirstLeg.get("sequenceNumber")
        origin                           = theFirstLeg.get("origin")
        destination                      = theFirstLeg.get("destination")
        serviceType                      = theFirstLeg.get("serviceType")
        aircraftOwner                    = theFirstLeg.get("aircraftOwner")
        aircraftType                     = theFirstLeg.get("aircraftType")
        aircraftConfigurationVersion     = theFirstLeg.get("aircraftConfigurationVersion")
        #registration                    = theFirstLeg.get("registration")  # Non utiulisé en V1
        #op                              = theFirstLeg.get("op")            # Non utilisé en V1
        aircraftDepartureTimeUTC         = theFirstLeg.get("aircraftDepartureTimeUTC")
        aircraftType                     = theFirstLeg.get("aircraftType")
        aircraftDepartureTimeDateDiffUTC = theFirstLeg.get("aircraftDepartureTimeDateDiffUTC")
        aircraftDepartureTimeLT          = theFirstLeg.get("aircraftDepartureTimeLT")
        aircraftDepartureTimeDateDiffLT  = theFirstLeg.get("aircraftDepartureTimeDateDiffLT")
        aircraftDepartureTimeVariation   = theFirstLeg.get("aircraftDepartureTimeVariation")
        aircraftArrivalTimeUTC           = theFirstLeg.get("aircraftArrivalTimeUTC")
        aircraftArrivalTimeDateDiffUTC   = theFirstLeg.get("aircraftArrivalTimeDateDiffUTC")
        aircraftArrivalTimeLT            = theFirstLeg.get("aircraftArrivalTimeLT")
        aircraftArrivalTimeDateDiffLT    = theFirstLeg.get("aircraftArrivalTimeDateDiffLT")
        aircraftArrivalTimeVariation     = theFirstLeg.get("aircraftArrivalTimeVariation")
    
        # On vérifie que le vol n'existe pas déjà en base
        if air_db.check_flight_passenger(airLine, flightNumber, startDateUTC, sequenceNumber, origin)[0][0] > 0:
            continue
        
        try:
            #print("Vol à insérer : ", flightNumber, " -- ", aircraftOwner, " -- " , startDateLT , " -- ", origin  ," -- ", destination, " -- ", airLine)
            # Insertion des données du vol dans la table FLIGHTS_SCHEDULES_PASSENGER
            cursor = cnx.cursor()
            prepareStatement_fsp   = "Insert into DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER (FSP_AIRLINE_FK, FSP_FLIGHT_NUMBER, FSP_START_DATE_UTC,"
            prepareStatement_fsp  += "FSP_END_DATE_UTC, FSP_START_DATE_LT, FSP_END_DATE_LT, FSP_DAYS_OF_OPERATIONS_UTC, FSP_DAYS_OF_OPERATIONS_LT ) values (%s,%s,%s,%s,%s,%s,%s,%s)"
            fspData = (airLine, flightNumber, utils.add_minutes_to_datetime(startDateUTC), utils.add_minutes_to_datetime(endDateUTC),
                       utils.add_minutes_to_datetime(startDateLT), utils.add_minutes_to_datetime(endDateLT), daysOfOperationUTC, daysOfOperationLT)
            cursor.execute(prepareStatement_fsp, fspData)

            # Récupération du dernier ID généré dans la table FLIGHTS_SCHEDULES_PASSENGER qui va servir de lien avec la table FLIGHTS_SCHEDULES_PASSENGER_LEGS
            theLastId = air_db.last_sequence_flight_passenger()[0][0]

            # Insertion des données du vol dans la table FLIGHTS_SCHEDULES_PASSENGER_LEGS
            prepareStatement_fspl  = "Insert into DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER_LEGS ( FSPL_ID, FSPL_SEQUENCE_NUMBER, FSPL_ORIGIN_AIRPORT_FK, "
            prepareStatement_fspl += "FSPL_DESTINATION_AIRPORT_FK, FSPL_SERVICE_TYPE, FSPL_OWNER,"
            prepareStatement_fspl += "FSPL_TYPE, FSPL_CONFIGURATION,  FSPL_DEPARTURE_DIFF_TIME_UTC, FSPL_DEPARTURE_DIFF_TIME_LT,"
            prepareStatement_fspl += "FSPL_ARRIVAL_DIFF_TIME_UTC, FSPL_ARRIVAL_DIFF_TIME_LT, "
            prepareStatement_fspl += "FSPL_DEPARTURE_TIME_UTC,FSPL_DEPARTURE_TIME_LT, "
            prepareStatement_fspl += "FSPL_ARRIVAL_TIME_UTC,FSPL_ARRIVAL_TIME_LT) "
            prepareStatement_fspl += "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            fsplData = (theLastId, 1, origin, destination, serviceType, aircraftOwner, aircraftType, aircraftConfigurationVersion,
                        aircraftDepartureTimeDateDiffUTC, aircraftDepartureTimeDateDiffLT,
                        aircraftArrivalTimeDateDiffUTC, aircraftArrivalTimeDateDiffLT ,
                        utils.add_minutes_to_datetime(startDateUTC, aircraftDepartureTimeUTC), utils.add_minutes_to_datetime(startDateUTC, aircraftDepartureTimeLT),
                        utils.add_minutes_to_datetime(endDateUTC, aircraftArrivalTimeUTC), utils.add_minutes_to_datetime(endDateUTC, aircraftArrivalTimeLT)
                       )
            
            cursor.execute(prepareStatement_fspl, fsplData)
            cursor.close()
 
        except Exception as e:
            print(e)
            print("Erreur : ", flightNumber, " -- ", aircraftOwner, " -- " , startDateLT , " -- ", origin  ," -- ", destination, " -- ", airLine)
            cnx.rollback()
            continue

        # Commit de la transaction par vol
        cnx.commit()


if __name__ == '__main__':
    # Récupération des données à partir du web service de l'API Lufthansa
    # Paramètre d'entrée "en dur" pour le moment
    airlines        = "LH"      # Dans la V1, on prend en compte uniquement LH

    #print ("Veuillez donner le nombre de jours que vous souhaitez récupérés depuis aujourd'hui : ")
    #numberOfDays = input();
    # On récupère les 2 derniers jours des vols
    numberOfDays = 2

    #print("Debut insertion : ", str(datetime.now()))

    listeOfDates =  u.get_list_formatted_dates(int(numberOfDays))

    for i in range(0,len(listeOfDates)-1):
        startDate, endDate = (listeOfDates[i], listeOfDates[i+1])
        insert_data_in_flights_schedules_tables_from_ws (airlines, startDate, endDate, days_of_operation="1234567", time_mode="UTC", origin="", destination="")

    #print("Fin insertion : ", str(datetime.now()))
