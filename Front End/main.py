
from flask import render_template, url_for, request
from app import webapp, memcache
from flask import json

@webapp.route('/')
def main():
    return render_template("home.html")


@webapp.route('/key', methods=['POST'])
def key():
    key = request.form.get('key')

    if key in memcache:
        value = memcache[key]
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@webapp.route('/statistics', methods=['POST'])
def statistics():
    return render_template("statistics.html")

@webapp.route('/config', methods=['POST'])
def config():
    return render_template("config.html")


@webapp.route('/retrieve_key_form', methods=['GET'])
def retrieve_key_form():
    return render_template("key_form.html")


@webapp.route('/upload_form', methods=['POST'])
def upload_form():
    return render_template("upload_form.html")


'''
@webapp.route('/upload', methods=['POST'])
def upload():

    key = request.form.get('key')
    value = request.form.get('value')
    memcache[key] = value

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response
'''

@webapp.route('/list_keys', methods=['POST'])
def list_keys():
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )
    return render_template("key_list.html", curData=memcache)

