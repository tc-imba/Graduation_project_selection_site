#!/bin/bash

apt-get install python3-pil
pip3 install tornado openpyxl PyYaml

if ! python3 -c "import mysql.connector" > /dev/null 2>&1; then
    wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.5.tar.gz
    tar -zxf mysql-connector-python-2.1.5.tar.gz
    (
        cd mysql-connector-python-2.1.5
        python3 setup.py install
    )
fi



#mysql -u"$username" -p"$password" "$dbName" < ./sample.dump