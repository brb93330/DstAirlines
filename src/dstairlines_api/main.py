import utils as u

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy import create_engine, and_, text
from sqlalchemy.sql.expression import join, select
from sqlalchemy.sql import func
from typing import Optional
from werkzeug.exceptions import BadRequest
import uvicorn


# Load the environment variables, to get the database connection info
load_dotenv()

VERSION_API = "1.0.0"

api = FastAPI(
    title='Projet DstAirlines - API de services',
    description="Statistiques les vols de la compagnie Lufthansa",
    version=VERSION_API
)


questions_responses = {
    200: {"description": "OK"},
    404: {"description": "Objet non trouvé"},
}


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    '''
    Permet de vérifier que le mot de passe saisi par l'utilisateur correspond bien à celui stocké dans le dictionnaire user
    '''
    username = credentials.username
    api_users = u.get_api_users()

    if not(api_users.get(username)) or not(pwd_context.verify(credentials.password, pwd_context.hash(api_users[username]['password']))):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="compte ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@api.get('/health', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    '''
    Permet de vérifier le bon fonctionnement des services.
    '''
    return {'healthcheck': 'OK'}


@api.get('/version', status_code=status.HTTP_200_OK)
def get_version():
    '''
     Retourne le numéro de version de l'API.
    '''
    return {"version": VERSION_API}


@api.get('/metrics', status_code=status.HTTP_200_OK)
def get_metrics():
    '''
    Retourne diverses métriques sur l'API.
    '''
    return {"metric1": "TO DO"}


@api.get('/v1/airline-delays/{airlineId}', name ="Liste des vols d\'une compagnie aérienne en retard", responses= questions_responses)
def get_line_delays(airlineId: str,
        departure_date: str = Query(..., description='Vols dont le jour de départ est supérieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230420)'), 
        arrival_date: str = Query(..., description='Vols dont le jour d\'arrivée est inférieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230424)'), 
        departure_airport: str = Query(default=None, description='Aéroport de départ (code sur 3 lettres)'), 
        arrival_airport: str = Query(default=None, description='Aéroport d\'arrivée (code sur 3 lettres)'), 
        delay: int = Query(60, description='Retard en minutes (>0)'),
        limit :Optional[int]= Query(100, description='Number of records returned per request. Defaults to 100, maximum is 1000 (if a value bigger than 100 is given, 100 will be taken)'), 
        offset :Optional[int]= Query(0, description='Number of records skipped'), 
        userName: str = Depends(get_current_user) ):
    '''
    Liste des vols d\'une compagnie aérienne en retard.
    '''

    user, pwd, host, port = u.get_database_connexion_config().get("user") , u.get_database_connexion_config().get("password"), u.get_database_connexion_config().get("host"), u.get_database_connexion_config().get("port")

    if delay == None or delay <0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nombre de minutes doit être strictement positif",
                headers={"WWW-Authenticate": "Basic"},
            )
    
    if departure_date == None or arrival_date == None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les dates de début et de fin doivent être renseignées",
                headers={"WWW-Authenticate": "Basic"},
            )
    
    formatted_departure_date = None
    try:
        formatted_departure_date = u.string_to_date(departure_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de début doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    formatted_end_date = None
    try:
        formatted_arrival_date= u.string_to_date(arrival_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    if departure_airport!=None and len(departure_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code de l'aéroport de départ est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if arrival_airport!=None and len(arrival_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code ded l'aéroport d\'arrivée est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if limit == None or limit <=0 or limit >1000:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit doit être strictement positif et inférieur ou égal à 1000",
                headers={"WWW-Authenticate": "Basic"},
            )

    if offset == None or offset <0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset doit être  positif ou égale à 0",
                headers={"WWW-Authenticate": "Basic"},
            )

    engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}")

    j1 = join(u.FLIGHTS_SCHEDULES_PASSENGER, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS,
         u.FLIGHTS_SCHEDULES_PASSENGER.FSP_ID == u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ID).join(u.OPERATIONS_FLIGHTS_STATUS, 
         and_(u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DEPARTURE_TIME_UTC == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_AIRLINE_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_FLIGHT_NUMBER == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_FLIGHT_NUMBER))
    
    w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.TIMESTAMPDIFF(text("MINUTE"), u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC )  >= delay,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_ACTUAL_TIME_UTC, '%Y%m%d') >= departure_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, '%Y%m%d') <= arrival_date
        )
    
    optional_criterias = ""
    if arrival_airport != None and departure_airport == None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.TIMESTAMPDIFF(text("MINUTE"), u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC )  >= delay,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_ACTUAL_TIME_UTC, '%Y%m%d') >= departure_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, '%Y%m%d') <= arrival_date
        )
    elif departure_airport != None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.TIMESTAMPDIFF(text("MINUTE"), u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC )  >= delay,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_ACTUAL_TIME_UTC, '%Y%m%d') >= departure_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, '%Y%m%d') <= arrival_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport
        )
    elif departure_airport == None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.TIMESTAMPDIFF(text("MINUTE"), u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC )  >= delay,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_ACTUAL_TIME_UTC, '%Y%m%d') >= departure_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, '%Y%m%') <= arrival_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )
    elif departure_airport != None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.TIMESTAMPDIFF(text("MINUTE"), u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC )  >= delay,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_ACTUAL_TIME_UTC, '%Y%m%d') >= departure_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, '%Y%m%d') <= arrival_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )

    stmt = select(u.FLIGHTS_SCHEDULES_PASSENGER, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK ) \
            .select_from(j1) \
            .where(w1).limit(limit).offset(offset)

    with engine.connect() as con:
        con.execute(text("USE " + u.get_database_connexion_config().get("database")))
        rs = con.execute(stmt)

        # Compteur
        stmt2 = select(text("count(1) as compteur") ) \
                .select_from(j1) \
                .where(w1)
        rs2 = con.execute(stmt2)

    columns = ["fspId", "airlineId", "flightNumber", "daysOfOperationsUtc", "startDateUtc", "endDateUtc", "daysOfOperationsLt", "startDateLt", "endDateLt",  "arrivalActualTimeUtc", "arrivalScheduledTimeUtc", "departureAirport",  "arrivalAirport" ]
    results = []
    for row in rs:
        results.append(dict(zip(columns, row)))

    total = {"total" : rs2.fetchone().__getattribute__("compteur")}
    results.append(total)

    '''
    Sur les bonnes pratiques (https://www.pythoniste.fr/python/fastapi/les-bonnes-pratiques-pour-construire-un-api-rest/) 
        15. Filtrer une Query avec un paramètre fields -> Pas nécessaire
        17. Toujours valider le Content-Type -> -> Pas nécessaire
    '''

    return results

@api.get('/v1/airline-canceled/{airlineId}', name ="Liste des vols d\'une compagnie aérienne annulés", responses= questions_responses)
def get_line_canceled(airlineId: str,
        start_date: str = Query(..., description='Vols dont le jour de départ est supérieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230420)'), 
        end_date: str = Query(..., description='Vols dont le jour d\'arrivée est inférieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230424)'), 
        departure_airport: str = Query(default=None, description='Aéroport de départ (code sur 3 lettres)'), 
        arrival_airport: str = Query(default=None, description='Aéroport d\'arrivée (code sur 3 lettres)'),
        limit :Optional[int]= Query(100, description='Number of records returned per request. Defaults to 100, maximum is 1000 (if a value bigger than 100 is given, 100 will be taken)'), 
        offset :Optional[int]= Query(0, description='Number of records skipped'), 
        userName: str = Depends(get_current_user) ):
    '''
    Liste des vols d\'une compagnie aérienne annulés.
    '''

    user, pwd, host, port = u.get_database_connexion_config().get("user") , u.get_database_connexion_config().get("password"), u.get_database_connexion_config().get("host"), u.get_database_connexion_config().get("port")
    
    if start_date == None or end_date == None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les dates de début et de fin doivent être renseignées",
                headers={"WWW-Authenticate": "Basic"},
            )
    
    formatted_departure_date = None
    try:
        formatted_departure_date = u.string_to_date(start_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de début doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    formatted_end_date = None
    try:
        formatted_arrival_date= u.string_to_date(end_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    if departure_airport!=None and len(departure_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code de l'aéroport de départ est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if arrival_airport!=None and len(arrival_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code ded l'aéroport d\'arrivée est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if limit == None or limit <=0 or limit >1000:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit doit être strictement positif et inférieur ou égal à 1000",
                headers={"WWW-Authenticate": "Basic"},
            )

    if offset == None or offset <0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset doit être  positif ou égale à 0",
                headers={"WWW-Authenticate": "Basic"},
            )

    engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}")

    j1 = join(u.FLIGHTS_SCHEDULES_PASSENGER, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS,
         u.FLIGHTS_SCHEDULES_PASSENGER.FSP_ID == u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ID).join(u.OPERATIONS_FLIGHTS_STATUS, 
         and_(u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DEPARTURE_TIME_UTC == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_AIRLINE_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_FLIGHT_NUMBER == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_FLIGHT_NUMBER))
    
    w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date
        )
    
    optional_criterias = ""
    if arrival_airport != None and departure_airport == None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date
        )
    elif departure_airport != None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport
        )
    elif departure_airport == None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )
    elif departure_airport != None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )

    stmt = select(u.FLIGHTS_SCHEDULES_PASSENGER, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK ) \
            .select_from(j1) \
            .where(w1).limit(limit).offset(offset)

    with engine.connect() as con:
        con.execute(text("USE " + u.get_database_connexion_config().get("database")))
        rs = con.execute(stmt)

        # Compteur
        stmt2 = select(text("count(1) as compteur") ) \
                .select_from(j1) \
                .where(w1)
        rs2 = con.execute(stmt2)

    columns = ["fspId", "airlineId", "flightNumber", "daysOfOperationsUtc", "startDateUtc", "endDateUtc", "daysOfOperationsLt", "startDateLt", "endDateLt",  "arrivalActualTimeUtc", "arrivalScheduledTimeUtc", "departureAirport",  "arrivalAirport" ]
    results = []
    for row in rs:
        results.append(dict(zip(columns, row)))

    total = {"total" : rs2.fetchone().__getattribute__("compteur")}
    results.append(total)

    '''
    Sur les bonnes pratiques (https://www.pythoniste.fr/python/fastapi/les-bonnes-pratiques-pour-construire-un-api-rest/) 
        15. Filtrer une Query avec un paramètre fields -> Pas nécessaire
        17. Toujours valider le Content-Type -> -> Pas nécessaire
    '''

    return results

@api.get('/v1/airline-landed/{airlineId}', name ="Liste des vols d\'une compagnie aérienne arrivés", responses= questions_responses)
def get_line_landed(airlineId: str,
        start_date: str = Query(..., description="Vols dont le jour de départ est supérieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230420)"), 
        end_date: str = Query(..., description="Vols dont le jour d'arrivée est inférieur à ce jour (Format YYYYMMDD, en UTC, ex: 20230424)"), 
        departure_airport: str = Query(default=None, description='Aéroport de départ (code sur 3 lettres)'), 
        arrival_airport: str = Query(default=None, description='Aéroport d\'arrivée (code sur 3 lettres)'),
        limit :Optional[int]= Query(100, description='Number of records returned per request. Defaults to 100, maximum is 1000 (if a value bigger than 100 is given, 100 will be taken)'), 
        offset :Optional[int]= Query(0, description='Number of records skipped'), 
        userName: str = Depends(get_current_user) ):
    '''
    Liste des vols d\'une compagnie aérienne ayant atterri.
    '''

    user, pwd, host, port = u.get_database_connexion_config().get("user") , u.get_database_connexion_config().get("password"), u.get_database_connexion_config().get("host"), u.get_database_connexion_config().get("port")
    
    if start_date == None or end_date == None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les dates de début et de fin doivent être renseignées",
                headers={"WWW-Authenticate": "Basic"},
            )
    
    formatted_departure_date = None
    try:
        formatted_departure_date = u.string_to_date(start_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de début doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    formatted_end_date = None
    try:
        formatted_arrival_date= u.string_to_date(end_date)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être renseignée sous le format YYYYMMDD. Ex: 20230420",
                headers={"WWW-Authenticate": "Basic"},
            )

    if departure_airport!=None and len(departure_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code de l'aéroport de départ est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if arrival_airport!=None and len(arrival_airport)!=3:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le code ded l'aéroport d\'arrivée est sur 3 lettres",
                headers={"WWW-Authenticate": "Basic"},
            )

    if limit == None or limit <=0 or limit >1000:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit doit être strictement positif et inférieur ou égal à 1000",
                headers={"WWW-Authenticate": "Basic"},
            )

    if offset == None or offset <0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset doit être  positif ou égale à 0",
                headers={"WWW-Authenticate": "Basic"},
            )

    engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}")

    j1 = join(u.FLIGHTS_SCHEDULES_PASSENGER, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS,
         u.FLIGHTS_SCHEDULES_PASSENGER.FSP_ID == u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ID).join(u.OPERATIONS_FLIGHTS_STATUS, 
         and_(u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_AIRPORT_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DEPARTURE_TIME_UTC == u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_AIRLINE_FK
            , u.FLIGHTS_SCHEDULES_PASSENGER.FSP_FLIGHT_NUMBER == u.OPERATIONS_FLIGHTS_STATUS.OFS_OPERATING_CARRIER_FLIGHT_NUMBER))
    
    w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date
        )
    
    optional_criterias = ""
    if arrival_airport != None and departure_airport == None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base nest "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'CD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date
        )
    elif departure_airport != None and arrival_airport == None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport
        )
    elif departure_airport == None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )
    elif departure_airport != None and arrival_airport != None:
        w1 = and_(
        u.FLIGHTS_SCHEDULES_PASSENGER.FSP_AIRLINE_FK == airlineId,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_DEPARTURE_SCHEDULED_TIME_UTC, '%Y%m%d')>='20230415', # La base n'est "correcte que depuis cette date"
        u.OPERATIONS_FLIGHTS_STATUS.OFS_FTS_FK == 'LD',
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') >= start_date,
        func.DATE_FORMAT(u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, '%Y%m%d') <= end_date,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK == departure_airport,
        u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK == arrival_airport
        )

    stmt = select(u.FLIGHTS_SCHEDULES_PASSENGER, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_ACTUAL_TIME_UTC, u.OPERATIONS_FLIGHTS_STATUS.OFS_ARRIVAL_SCHEDULED_TIME_UTC, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_ORIGIN_AIRPORT_FK, u.FLIGHTS_SCHEDULES_PASSENGER_LEGS.FSPL_DESTINATION_AIRPORT_FK ) \
            .select_from(j1) \
            .where(w1).limit(limit).offset(offset)

    with engine.connect() as con:
        con.execute(text("USE " + u.get_database_connexion_config().get("database")))
        rs = con.execute(stmt)

        # Compteur
        stmt2 = select(text("count(1) as compteur") ) \
                .select_from(j1) \
                .where(w1)
        rs2 = con.execute(stmt2)

    columns = ["fspId", "airlineId", "flightNumber", "daysOfOperationsUtc", "startDateUtc", "endDateUtc", "daysOfOperationsLt", "startDateLt", "endDateLt",  "arrivalActualTimeUtc", "arrivalScheduledTimeUtc", "departureAirport",  "arrivalAirport" ]
    results = []
    for row in rs:
        results.append(dict(zip(columns, row)))

    total = {"total" : rs2.fetchone().__getattribute__("compteur")}
    results.append(total)

    '''
    Sur les bonnes pratiques (https://www.pythoniste.fr/python/fastapi/les-bonnes-pratiques-pour-construire-un-api-rest/) 
        15. Filtrer une Query avec un paramètre fields -> Pas nécessaire
        17. Toujours valider le Content-Type -> -> Pas nécessaire
    '''

    return results

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)