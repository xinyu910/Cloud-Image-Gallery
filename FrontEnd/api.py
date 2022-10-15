import base64
from flask import render_template, url_for, request, g
from FrontEnd import webapp
from flask import json
from FrontEnd.main import get_db, allowed_file
import os
from werkzeug.utils import secure_filename
import requests


@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    """Return list_keys response"""
    try:
        cnx = get_db()
        cursor = cnx.cursor()
        query = ''' SELECT image_key, image_path
                        FROM images;
                    '''
        cursor.execute(query)
        rows = cursor.fetchall()
        data = {
            "success": "true",
            "keys": [i[0] for i in rows]
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json')
        cnx.close()
        return response
    except:
        data = {
            "success": "false",
            "error": {
                "code": 500,
                "message": "Internal error, unable to get the keys"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=500,
            mimetype='application/json')
        return response


@webapp.route('/api/upload', methods=['POST'])
def apiUpload():
    """
    Upload the key image pair. Store the image in local filesystem and put the file location in the database
    calls invalidatekey in memcache
    Returns: response object fot test
    """
    image_key = request.form.get('key')
    image_file = request.files.get('file', '')

    # check if file is empty
    if image_file.filename == '' or image_key == '':
        data = {
            "success": "false",
            "error": {
                "code": 400,
                "message": "image file or key is not given"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json')
        return response

    # check if the uploaded file type is allowed
    if not allowed_file(image_file.filename):
        data = {
            "success": "false",
            "error": {
                "code": 400,
                "message": "File type is not supported"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json')
        return response

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_key = %s'''
    cursor.execute(has_key, (image_key,))

    # path to save the image
    folder = webapp.config['UPLOAD_FOLDER']
    if not os.path.isdir(folder):
        os.mkdir(folder)
    filename = os.path.join(folder, secure_filename(image_file.filename))
    filename = filename.replace('\\', '/')

    rows = cursor.fetchall()
    # if the database has the key, delete the associated image in the file system
    # and replace the old file location in the database with the new one
    if rows:
        image_file.save(filename)
        path_to_delete = rows[0][0]
        if os.path.isfile(path_to_delete):
            os.remove(path_to_delete)
        query = '''UPDATE images SET image_path = %s WHERE image_key = %s'''
        cursor.execute(query, (filename, image_key))
        cnx.commit()
    # if database doesn't have the key, insert key, image pair into it.
    else:
        # if duplicate file name found, add number after
        count = 1
        if os.path.isfile(filename):
            index = filename.rfind(".")
            filename = filename[:index] + str(count) + filename[index:]
        while os.path.isfile(filename):
            count = count + 1
            index = filename.rfind(".")
            filename = filename[:index - 1] + str(count) + filename[index:]
        image_file.save(filename)
        query = ''' INSERT INTO images (image_key, image_path) VALUES (%s,%s)'''
        cursor.execute(query, (image_key, filename))
        cnx.commit()

    cnx.close()
    # invalidate key in memcache
    dataSend = {"key": image_key}
    res = requests.post('http://localhost:5001/invalidateKey', json=dataSend)
    if res.status_code != 200:
        data = {
            "success": "false",
            "error": {
                "code": 500,
                "message": "Invalidate key error"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=500,
            mimetype='application/json')
        return response
    else:
        data = {
            "success": "true"
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json')

        return response


@webapp.route('/api/key/<string:key_value>', methods=['GET'])
def apikey(key_value):
    image_key = key_value
    if image_key == '':
        data = {
            "success": "false",
            "error": {
                "code": 400,
                "message": "Image Key is not given"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json')
        return response

    # # find if this key image pair is in memcache, if so, retrieve and render it directly from cache.
    dataSend = {"key": image_key}
    res = requests.post('http://localhost:5001/GET', json=dataSend)
    if res.status_code == 200:
        data = {
            "success": "true",
            "content": res.json()['content']
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        # if not in cache, get from database and call put in memcache
        cnx = get_db()
        cursor = cnx.cursor()

        # check if database has the key or not
        has_key = ''' SELECT image_path FROM images WHERE image_key = %s'''

        cursor.execute(has_key, (image_key,))
        rows = cursor.fetchall()
        cnx.close()

        # database has the key, store the image key and the encoded image content pair in cache for next retrieval
        if rows:
            path = rows[0][0]
            path = path.replace('\\', '/')
            base64_image = base64.b64encode(open(path, "rb").read()).decode('utf-8')
            dataSend = {"key": image_key, "image": base64_image}
            res = requests.post('http://localhost:5001/PUT', json=dataSend)
            if res.status_code != 200:
                data = {
                    "success": "false",
                    "error": {
                        "code": 500,
                        "message": "Internal Error, memcache put error"
                    }}
                response = webapp.response_class(
                    response=json.dumps(data),
                    status=500,
                    mimetype='application/json'
                )
            else:
                data = {
                    "success": "true",
                    "content": base64_image
                }
                response = webapp.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json'
                )
        else:
            data = {
                "success": "false",
                "error": {
                    "code": 404,
                    "message": "Unknown key"
                }}
            response = webapp.response_class(
                response=json.dumps(data),
                status=404,
                mimetype='application/json'
            )

        return response
