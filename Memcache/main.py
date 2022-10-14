from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
import datetime
from Memcache import webapp, memcache
import sys
import random
import mysql.connector
from Memcache.config import db_config
from Memcache.memcache_stat import Stats
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json

'''INIT'''
global memcacheConfig
global cacheState
cacheState = Stats()  # currently testing, use cacheState.hit cacheState.miss for hit/miss rate


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
    global memcacheConfig
    memcacheConfig = {'capacity': rows[0][0], 'policy': rows[0][1]}


def refresh_stat():
    with webapp.app_context():
        numOfItem = len(memcache.keys())
        totalSize = cacheState.total_image_size
        numOfRequests = cacheState.reqServed_num
        if (cacheState.hitCount == 0) and (cacheState.missCount == 0):
            missRate = 0
            hitRate = 0
        else:
            hitmiss = cacheState.missCount + cacheState.hitCount
            missRate = cacheState.missCount / hitmiss
            hitRate = cacheState.hitCount / hitmiss

        now = datetime.datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        cnx = get_db()
        cursor = cnx.cursor()

        query = '''INSERT INTO statistics (numOfItem, totalSize, numOfRequests, 
                                missRate, hitRate, time_stamp) VALUES (%s,%s,%s,%s,%s,%s)'''
        cursor.execute(query, (numOfItem, totalSize, numOfRequests, missRate, hitRate, now))
        print("success", now)
        cnx.commit()
        cnx.close()


with webapp.app_context():
    get_config()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=refresh_stat, trigger="interval", seconds=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


def subinvalidatekey(key):
    """invalidatekey in memcache when needed"""
    # request+1
    cacheState.reqServed_num += 1

    if key in memcache:
        memcache.pop(key, None)
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


"""replacement policies"""


def dictLRU():
    """LRU: remove the oldest key in memcache"""
    OldTimeStamp = min([d['time'] for d in memcache.values()])
    oldestKey = ""
    for key in memcache.keys():
        if memcache[key]['time'] == OldTimeStamp:
            oldestKey = key  # find oldest key
    # image size deducted
    cacheState.total_image_size = cacheState.total_image_size - sys.getsizeof(memcache[oldestKey]['content'])
    del memcache[oldestKey]  # delete oldest key


def dictRandom():
    """Remove a key randomly"""
    keys = list(memcache.keys())
    keyIndex = random.randint(0, len(keys) - 1)
    # image size deducted
    cacheState.total_image_size = cacheState.total_image_size - sys.getsizeof(memcache[keys[keyIndex]]['content'])
    del memcache[keys[keyIndex]]  # delete the random key


def fitCapacity(extraSize):
    """if the given size exceeded cache capacity, delete keys based on selected policy"""
    print("before ", memcache.keys())
    print(cacheState.total_image_size)
    while (extraSize + cacheState.total_image_size) > memcacheConfig['capacity'] * 1048576 and bool(memcache):
        # capacity full
        print("Error: Larger than capacity, remove one")
        if memcacheConfig['policy'] == "LRU":
            dictLRU()
        else:
            dictRandom()
    print("after ", memcache.keys())
    print(cacheState.total_image_size)


def subPUT(key, value):
    """
    :param key: key
    :param value: base64 image
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

    if not value:
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
    image_size = sys.getsizeof(value)
    if image_size > memcacheConfig['capacity'] * 1048576:
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

    # subinvalidatekey(key)  # remove key if the key is already in the cache

    fitCapacity(image_size)  # fit capacity
    # add the key image pair in the cache
    memcache[key] = {'content': value, 'time': datetime.datetime.now()}
    cacheState.total_image_size = cacheState.total_image_size + image_size
    print("final ", memcache.keys())
    print(cacheState.total_image_size)
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def subGET(key):
    # request+1
    cacheState.reqServed_num += 1

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
        cacheState.missCount +=1
        return response
    else:
        # timestamp update
        memcache[key]['time'] = datetime.datetime.now()
        data = {
            "success": "true",
            "content": memcache[key]['content']
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        # hit
        # cacheState.listOfStat.append(("hit", datetime.datetime.now()))
        cacheState.hitCount +=1
        return response


def subCLEAR():
    # request+1
    cacheState.reqServed_num += 1
    cacheState.total_image_size = 0
    cacheState.numOfItem = 0
    memcache.clear()
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    return "welcome"


@webapp.route('/GET', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    return subGET(key)


@webapp.route('/PUT', methods=['POST'])
def PUT():
    key = request.json["key"]
    image = request.json["image"]
    return subPUT(key, image)


@webapp.route('/invalidateKey', methods=['POST', 'GET'])
def invalidateKey():
    key = request.json["key"]
    return subinvalidatekey(key)


@webapp.route('/refreshConfiguration', methods=['POST'])
def refreshConfiguration():
    # request+1
    cacheState.reqServed_num += 1
    clear_result = request.json['clear']
    get_config()
    # clear cache if needed or change memcache based on new capacity (reduce memcache if new capacity is smaller)
    if clear_result == 'Yes':
        subCLEAR()
    else:
        fitCapacity(0)
    data = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    webapp.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
