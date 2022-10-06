import os

from flask import jsonify
from app import webapp, memcache, memcacheConfig, Stats, EachStat
from app.Config import Config
import datetime
import json


def _clrCache(folderPath=Config.MEMCACHE_FOLDER):
    """
    clear all chache
    :return: if action success
    :type folderPath: object
    """
    message = "OK"
    return jsonify({"statusCode": 200,
                    "message": message})

def _deltCache(key, folderPath=Config.MEMCACHE_FOLDER):
    """
    delet a cache according to the key
    :param key:
    :param folderPath:
    :return:
    """
    state = ''
    return state

def CacheInsert(key, name):
    if key and name:
        memcache[key] = {'name': name, 'time': datetime.datetime.now()}

def statistic():

def PUT(key, name, path):
    pass

def GET(key):
    pass

@ webapp.route('/clear')
def CLEAR():
    """API function for dropping all keys and values
    """
    _clrCache(folderPath=Config.MEMCACHE_FOLDER)
    message = "OK"
    return jsonify({"statusCode": 200,
                    "message": message})

@ webapp.route('/SOME PAGES')

def INVALID(key):
    """
    API function drop invalid key
    :param key:
    """
@ webapp.route('/SOME PAGES')
def REFRESHConfig():
    """
    API Function call to read mem-cache related details from the database
    and reconfigure it with default values
    """

