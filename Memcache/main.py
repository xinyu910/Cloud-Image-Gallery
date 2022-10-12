# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
from werkzeug.utils import secure_filename
import os
import datetime
from datetime import timedelta
import base64
#from memcache_stat import Stats, SingleStat, eachState, cacheTotalState
from Memcache import webapp as app, memcache
import sys
import random
import mysql.connector
from Memcache.config import db_config

app.app_context().push()

# config from the db
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
global memcacheConfig

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


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_config():
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''SELECT capacity, policy
                    FROM configurations WHERE config_id = 1;
                '''
    cursor.execute(query)
    rows = cursor.fetchall()
    cnx.close()
    return {'capacity': rows[0][0], 'policy': rows[0][1]}


memcacheConfig = get_config()

"""///////////////////////////////////FOR PUT METHOD///////////////////////////////////"""
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def saveDict(key, image_Binary):   
    #image_Binary = f.read()
    """imageBase64Encode = base64.b64encode(image_Binary).decode('utf-8')
    memcache[key] = {'content': imageBase64Encode, 'time': datetime.datetime.now()}
    """
    memcache[key] = {'content': image_Binary, 'time': datetime.datetime.now()}

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
def invalidatekey(user_input):
    if memcache.has_key(user_input):
        memcache.delete(user_input)
    data = {"success": "true"}
    response = app.response_class(
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
    while((currentSize) > memcacheConfig['capacity']):
        #capacity full
        print("Error: Larger than capacity, remove one")
        if (memcacheConfig['capacity'] == "LRU"):
            dictLRU()
        else:
            dictRandom()


def PUT(user_input, image_file):
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
    if not (f and allowed_file(image_file.filename)):
        data = {"success": "false",
                "error": {
                    "code": 400,
                    "message": "Error: wrong file type, expecting png, jpg, JPG, PNG, bmp"
                }}
        response = app.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json'
            )
        return response

    invalidatekey(user_input)# remove 
    fitCapacity(capacitySum() + (sys.getsizeof(image_file)/1048576))#fit capacity 字典满了
    saveDict(user_input, image_file)# add
    data = {"success": "true"}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def GET(user_input):
    if user_input not in memcache.keys():
        data = {"success": "false",
            "error": {
                "code": 404,
                "message": "Unknown Key"
            }}
        response = app.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
            )
        return response
    else:
        #timestemp update
        memcache[user_input]['time'] = datetime.datetime.now()
        data = {
            "success": "true",
            "content": memcache[user_input]['content']
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response


#   没试过
def CLEAR():
    clearCache()
    data = {"success": "true"}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def refreshConfiguration():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
