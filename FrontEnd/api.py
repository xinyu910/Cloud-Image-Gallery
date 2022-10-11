import base64
from flask import render_template, url_for, request, g
from FrontEnd import webapp, key_image
from flask import json
from FrontEnd.main import get_db
import os
from werkzeug.utils import secure_filename


@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    """Return list_keys response, for api endpoint test"""
    cnx = get_db()

    cursor = cnx.cursor()

    query = ''' SELECT image_id, image_path
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


@webapp.route('/api/upload', methods=['POST'])
def apiUpload():
    """
    Upload the key image pair. Store the image in local filesystem and put the file location in the database
    Returns: response object fot test
    """
    image_key = request.form.get('key')
    image_file = request.files.get('file', '')

    # check if file is empty
    if image_file.filename == '' or image_key == '':
        data = {
            "success": "false",
            "error": {
                "code": 500,
                "message": "image file or key is not given from form"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json')
        return response

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_id = %s'''

    cursor.execute(has_key, (image_key,))

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
        query = '''UPDATE images SET image_path = %s WHERE image_id = %s'''
        cursor.execute(query, (filename, image_key))
        cnx.commit()
    else:
        # if duplicate file name found, add number after
        count = 1
        if os.path.isfile(filename):
            index = filename.rfind(".")
            filename = filename[:index]+str(count)+filename[index:]
        while os.path.isfile(filename):
            count = count+1
            index = filename.rfind(".")
            filename = filename[:index-1] + str(count) + filename[index:]
        image_file.save(filename)
        query = ''' INSERT INTO images (image_id, image_path) VALUES (%s,%s)'''
        cursor.execute(query, (image_key, filename))
        cnx.commit()

    cnx.close()
    key_image[image_key] = filename

    data = {
        "success": "true"
    }
    response = webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json')

    return response


@webapp.route('/api/key/<key_value>', methods=['POST'])
def apiKey(key_value):
    # image_key = request.form.get('key')
    # not sure
    image_key = key_value
    if image_key == '':
        data = {
            "success": "false",
            "error": {
                "code": 500,
                "message": "Image Key is not given from form"
            }}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json')
        return response

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_id = %s'''

    cursor.execute(has_key, (image_key,))

    rows = cursor.fetchall()

    if rows:
        path = rows[0][0]
        path = path.replace('\\', '/')
        path = rows[0][0]
        path = path.replace('\\', '/')
        index = path.find('/')
        path = path[index + 1:]
        path = os.path.join('./../', path)
        base64_image = base64.b64encode(open(path, "rb").read()).decode('utf-8')
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
                "code": 400,
                "message": "Unknown key"
         }
}
        response = webapp.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json'
        )

    return response


