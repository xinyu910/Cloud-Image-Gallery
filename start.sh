#!/bin/bash

pip install -r requirements.txt
rm -r FrontEnd/static/images
mysql --user=root --password=ece1779pass -p memcache < database.sql
python "run.py"