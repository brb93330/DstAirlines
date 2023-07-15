#!/bin/sh

count=$(docker ps -a --no-trunc |grep mysqlcontainer |grep Up |wc -l);
if [ $count -ne 1 ];
then
	docker start mysqlcontainer
fi

count=$(docker ps -a --no-trunc |grep dashboard-dstairlines |grep Up |wc -l);
if [ $count -ne 1 ];
then
        docker start dashboard-dstairlines
fi

count=$(docker ps -a --no-trunc |grep lufthansa-analysis-api |grep Up |wc -l);
if [ $count -ne 1 ];
then
        docker start lufthansa-analysis-api
fi

