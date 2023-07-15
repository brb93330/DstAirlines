Description de l'arborescence :

A. /Documents/ : Point d'entrée pour présenter le projet Dstairlines --> A lire en premier pour comprendre l'objectif du projet

B. /Base_données/ : Elements pour installer et initialiser la base de données du projet 

C. /src/: Les programmes de l'application
	1. dashboard : Contient le programme pour le dashboard mis à disposition d'utilisateurs s'appuyant sur les données de la base de données Mysql
	2. db_update : Mise à jour de la BD avec les données des vols planifiés et les données réelles (vols arrivés ou annulés)
	3. dstairlines_api : api mise en place par le projet pour permettre d'interroger la base de données.
	4. dockerfiles : fichiers docker associés

D. /lanceur/ : Programmes à lancer via crontab (à faire manuellement sujr l'instance...)
	1. mise_a_jour_statut_vols : Appels à l'API Lufthansa afin de mettre à jour les données des vols qui ont été planifiés. 
	2. mise_a_jour_vols_planifies : : Appels à l'API Lufthansa afin de récupérer la lsite des vols planifiés.
	3. lance_mysql_container : Contrainte interne car l'instance s'arrête toutes les 3 heures. On relance automatiquement l'instance...

E. /Api_Lufthansa/ : Informations tirées du site de l'API lufthansa (https://developer.lufthansa.com/io-docs#)



F. /logs/ : Répertoire à créer pour logger des services
