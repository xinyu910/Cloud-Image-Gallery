from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
import os
import datetime
from datetime import timedelta
import base64
from Memcache import webapp, memcache
import sys
import random
import mysql.connector
from Memcache.config import db_config
from Memcache.memcache_stat import Stats

import json
import time
from time import sleep
from threading import Thread
#搜索注释????????是昨天写的内容非常不确定 
"""///////////////////////////////////INIT////////////////////////////////////////"""
# config from the db
global memcacheConfig
global cacheState
cacheState = Stats() #currently testing, use cacheState.hit cacheState.miss for hit/miss rate

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_config():
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''SELECT capacity, policy
                    FROM configurations WHERE config_id = 1;'''
                    
    cursor.execute(query)
    rows = cursor.fetchall()
    cnx.close()
    return {'capacity': rows[0][0], 'policy': rows[0][1]}
#/////////////我真的不是很会SQL救救我?????????????????????????????????????
def refresh_stat():
    """
    TABLE statistics(id int NOT NULL AUTO_INCREMENT,
                        numOfItem int NOT NULL,
                        totalSize int NOT NULL,
                        numOfRequests int NOT NULL,
                        missRate DECIMAL NOT NULL,
                        hitRate DECIMAL NOT NULL,
                        PRIMARY KEY (id));
    """
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''INSERT INTO cache_stats (numOfItem, totalSize, numOfRequests, 
                            missRate, hitRate ) VALUES (%d,%d,%d,%d,%d)'''
    numOfItem = len(memcache.keys())
    totalSize = cacheState.hit + cacheState.miss
    numOfRequests = cacheState.reqServed_num
    if ((cacheState.hit == 0) and (cacheState.miss == 0)):
        missRate = 0
        hitRate = 0
        
    else:
        missRate = cacheState.miss/totalSize
        hitRate = cacheState.hit/totalSize
        
    cursor.execute(query, (numOfItem, totalSize, numOfRequests, missRate, hitRate))  


    rows = cursor.fetchall()
    cnx.close()
    return {'capacity': rows[0][0], 'policy': rows[0][1]}


with webapp.app_context():
    memcacheConfig = get_config()


"""///////////////////////////////////FOR DELET METHOD///////////////////////////////////"""

def clearCache():
    """ for image in os.listdir(os.path.join(base_path, 'static/image')):
        print("Trying to delete ", image)
        for filetype in ALLOWED_EXTENSIONS:
            if image.endswith(filetype):
                print("Deleting ", image)
                os.remove(os.path.join(base_path, 'static/image', image))"""
    print("clean all cache")
    memcache.clear()


"""/////////////////////////////////////CAPACITY CALC/////////////////////////////////////"""

def capacitySum():
    """get the capacity of the dict"""
    sizeMB = sys.getsizeof(memcache)/1048576
    return sys.getsizeof(memcache)

""""//////////////////////////////////invalidatekey////////////////////////////////////////"""

#   delete same key
def subinvalidatekey(user_input):
    # request+1
    cacheState.reqServed_num += 1

    if user_input in memcache:
        memcache.delete(user_input)
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

"""/////////////////////////////////replacement policies/////////////////////////////////"""

def dictLRU():
    OldTimeStamp = min([d['time'] for d in memcache.values()])
    LRU = ""
    for key in memcache.keys():
        if memcache[key]['timestamp'] == OldTimeStamp:
            oldestKey = key #find oldest key
            
    memcache.delete(oldestKey)# delete oldest key


def dictRandom():
    keys = list(memcache.keys())
    keyIndex = random.randint(0, len(keys)-1)

    memcache.delete(keys[keyIndex]) # randomly delete


def fitCapacity(currentSize):
    while((currentSize) > memcacheConfig['capacity'] and bool(memcache)):
        #capacity full
        print("Error: Larger than capacity, remove one")
        if (memcacheConfig['capacity'] == "LRU"):
            dictLRU()
        else:
            dictRandom()
"""////////////////////////////////////////STAT//////////////////////////////////////////"""
def changeStat():
    # ... write db here ...
    cacheState.countStat()# calc stat
    refresh_stat()# refresh database?????????????????????????????????????
    print(cacheState.miss,"-",cacheState.hit)

def caller(callback_func, first=True):

    callback_func()
    sleep(5)
    caller(callback_func, False)

thread = Thread(target=caller, args=(changeStat,))
thread.start()# start refreshing

"""/////////////////////////////////////////OUTER////////////////////////////////////////"""
def subPUT(key, value):
    """
    :param user_input: key
    :param imagename: name of the image
    :return:
        json: "success": "false",
            "error": {
                "code": servererrorcode
                "message": errormessage
                }
    """
    """file type error"""
    # request+1
    cacheState.reqServed_num += 1

    if not (value):
        data = {"success": "false",
                "error": {
                    "code": 400,
                    "message": "Error: unsupported file type"
                }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json'
            )
        return response
    image_size = sys.getsizeof(value)/1048576
    if (image_size > memcacheConfig['capacity']):
        data = {"success": "false",
                "error": {
                    "code": 400,
                    "message": "Error: file size exceed capacity"
                }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json'
            )
        return response

    subinvalidatekey(key)# remove 
    fitCapacity(capacitySum() + (sys.getsizeof(value)/1048576) + sys.getsizeof(key))#fit capacity 
    # add
    memcache[key] = {'content': value, 'time': datetime.datetime.now()}
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    print(memcache[key]['time'])
    
    return response


def subGET(key):
    # request+1
    cacheState.reqServed_num += 1

    print(len(memcache))
    if key not in memcache.keys():
        data = {"success": "false",
            "error": {
                "code": 404,
                "message": "Unknown Key"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
            )

        # miss
        cacheState.listOfStat.append("miss")  
        cacheState.listOfTime.append(datetime.datetime.now())
        return response
    else:
        #timestemp update
        memcache[key]['time'] = datetime.datetime.now()
        data = {
            "success": "true",
            "content": memcache[key]['content']
        }
        print("found")
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        # hit
        cacheState.listOfStat.append("hit")  
        cacheState.listOfTime.append(datetime.datetime.now())
        return response


def subCLEAR():
    # request+1
    cacheState.reqServed_num += 1

    clearCache()
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def refreshConfiguration():
    pass


@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    return "welcome"


@webapp.route('/invalidateKey', methods=['POST'])
def invalidateKey():
    key = request.json["key"]
    return subinvalidatekey(key)


@webapp.route('/GET', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    return subGET(key)


@webapp.route('/PUT', methods=['POST'])
def PUT():
    key = request.json["key"]
    image = request.json["image"]
    return subPUT(key, image)

