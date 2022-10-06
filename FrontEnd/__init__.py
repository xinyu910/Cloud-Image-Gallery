from flask import Flask

global memcache

webapp = Flask(__name__)
memcache = {}

from FrontEnd import main




