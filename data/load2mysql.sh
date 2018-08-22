#!/bin/bash

host=localhost
port=3306
user=root
passwd=buptlida
databases=rentinfo
sql="delete from region;delete from street; delete from subline; delete from subway"
mysql -h$host -P${port} -u$user -p$passwd -N -e "$sql" $databases
sql="load data local infile 'areanum.txt' replace into table region fields terminated by '\t' (regionname, code);"
echo $sql
mysql -h$host -P${port} -u$user -p$passwd -N -e "$sql" $databases

sql="load data local infile 'subareanum.txt' replace into table street fields terminated by '\t' (streetname, code);"
echo $sql
mysql -h$host -P${port} -u$user -p$passwd -N -e "$sql" $databases

sql="load data local infile 'subwaysnum.txt' replace into table subline fields terminated by '\t' (linename, code);"
echo $sql
mysql -h$host -P${port} -u$user -p$passwd -N -e "$sql" $databases

sql="load data local infile 'subwaynum.txt' replace into table subway fields terminated by '\t' (name, code);"
echo $sql
mysql -h$host -P${port} -u$user -p$passwd -N -e "$sql" $databases


