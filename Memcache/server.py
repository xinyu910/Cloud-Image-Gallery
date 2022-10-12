from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import mysql.connector
from Memcache import webapp as app
from main import put, invalidatekey, get

@app.route('/', methods=['POST', 'GET'])
def welcome():
    return "welcome"


@app.route('/invalidateKey', methods=['POST', 'GET'])
def invalidateKey():
    key = request.json["key"]
    return invalidatekey(key)


@app.route('/GET', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    return get(key)


@app.route('/PUT', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    image = request.json["image"]
    return put(key, image)

