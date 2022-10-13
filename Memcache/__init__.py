"""
Memcache

"""

from flask import Flask

global memcache
global cacheStat
webapp = Flask(__name__)

memcache = {}

from Memcache import main


