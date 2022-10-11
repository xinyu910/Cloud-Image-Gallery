from flask import Flask
from FrontEnd.config import db_config

global key_image

webapp = Flask(__name__)

key_image = {}

from FrontEnd import main




