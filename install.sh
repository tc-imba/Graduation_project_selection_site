#!/bin/bash

apt-get install python3-pil
pip3 install tornado openpyxl PyYaml mysql-connector==2.1.6

#mysql -u"$username" -p"$password" "$dbName" < ./sample.dump