-- Nombre d'atterrissages par jour (depuis le 30 mars 2023)
select DATE_FORMAT(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC,'%Y%m%d') as 'Jour arrivée', ofs.OFS_FTS_FK , count(1) AS 'Nombre'
from DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ofs
where DATE_FORMAT(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC,'%Y%m%d') >= '20230330' and ofs.OFS_FTS_FK ='LD'
group by DATE_FORMAT(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC,'%Y%m%d') , ofs.OFS_FTS_FK
order by DATE_FORMAT(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC,'%Y%m%d') , ofs.OFS_FTS_FK;

-- Liste des vols dont le retard à l'arrivée est supérieur à 02 heures depuis le 30 mars 2023
select FSP_FLIGHT_NUMBER as 'Vol', fspl.FSPL_ORIGIN_AIRPORT_FK as 'Provenance', fspl.FSPL_DESTINATION_AIRPORT_FK as 'Destination',
       ofs.OFS_ARRIVAL_SCHEDULED_TIME_UTC as 'Arrivée', ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC as 'Arrivée UTC',
       HOUR(TIMEDIFF(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC , ofs.OFS_ARRIVAL_SCHEDULED_TIME_UTC)) as diff_hour
from DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER fsp
inner join DSTAIRLINES.FLIGHTS_SCHEDULES_PASSENGER_LEGS fspl on fsp.fsp_id = fspl.fspl_id
inner join DSTAIRLINES.OPERATIONS_FLIGHTS_STATUS ofs on 
    (ofs.OFS_DEPARTURE_AIRPORT_FK = fspl.FSPL_ORIGIN_AIRPORT_FK
	and ofs.OFS_ARRIVAL_AIRPORT_FK = fspl.FSPL_DESTINATION_AIRPORT_FK
	and ofs.OFS_DEPARTURE_SCHEDULED_TIME_UTC = fspl.FSPL_DEPARTURE_TIME_UTC
	and ofs.OFS_OPERATING_CARRIER_AIRLINE_FK = fsp.FSP_AIRLINE_FK
	and ofs.OFS_OPERATING_CARRIER_FLIGHT_NUMBER = fsp.FSP_FLIGHT_NUMBER
)
where DATE_FORMAT(ofs.OFS_DEPARTURE_SCHEDULED_TIME_UTC,'%Y%m%d') >= '20230330' and ofs.OFS_FTS_FK = 'LD'
and HOUR (TIMEDIFF(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC , ofs.OFS_ARRIVAL_SCHEDULED_TIME_UTC)) >=2
order by HOUR(TIMEDIFF(ofs.OFS_ARRIVAL_ACTUAL_TIME_UTC , ofs.OFS_ARRIVAL_SCHEDULED_TIME_UTC)) asc
;

-- Nombre de villes répertoriées
select count(1) from DSTAIRLINES.CITIES;
