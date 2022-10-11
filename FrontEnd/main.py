import base64
import os
import mysql.connector
from flask import render_template, request, g, redirect, url_for
from werkzeug.utils import secure_filename

from FrontEnd import webapp, key_image
from FrontEnd.config import db_config

UPLOAD_FOLDER = 'FrontEnd/static/images'
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


@webapp.route('/')
def home():
    """Render Homepage, returns: home page html"""
    return render_template("home.html")


@webapp.route('/success')
def success():
    """Render success page"""
    msg = request.args.get('msg')
    return render_template("success.html", msg=msg)


@webapp.route('/failure')
def failure():
    """Render error page"""
    msg = request.args.get('msg')
    return render_template("failure.html", msg=msg)


@webapp.route('/listKeys', methods=['GET'])
def listKeys():
    """Display the html page that shows all the keys in the database"""
    cnx = get_db()

    cursor = cnx.cursor()

    query = ''' SELECT image_id, image_path
                    FROM images;
                '''

    cursor.execute(query)
    rows = cursor.fetchall()

    cnx.close()

    return render_template("key_list.html", cursor=rows)


@webapp.route('/retrieve_key_form', methods=['GET'])
def retrieve_key_form():
    """Display an empty HTML form that allows users to browse image by key"""
    return render_template("key_form.html")


@webapp.route('/key', methods=['POST'])
def key():
    image_key = request.form.get('key')

    if image_key == '':
        return redirect(url_for('failure', msg="Key is not given or not given from form"))

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_id = %s'''

    cursor.execute(has_key, (image_key,))

    rows = cursor.fetchall()
    cnx.close()

    if rows:
        path = rows[0][0]
        path = path.replace('\\', '/')
        index = path.find('/')
        path = path[index + 1:]
        path = os.path.join('./../', path)
        return render_template('show_image.html', key=image_key, path=path), 200
    else:
        return redirect(url_for('failure', msg="Unknown Key"))

    return response


@webapp.route('/statistics', methods=['GET'])
def statistics():
    return render_template("statistics.html")


@webapp.route('/config', methods=['GET'])
def config():
    cnx = get_db()
    cursor = cnx.cursor()

    cursor.execute("SELECT capacity, policy FROM configurations WHERE config_id = 1")

    rows = cursor.fetchall()
    cnx.close()
    return render_template("config.html", capacity=rows[0][0], policy=rows[0][1])


@webapp.route('/update_config', methods=['POST'])
def update_config():
    capacity_result = int(request.form.get('capacity'))
    policy_result = request.form.get('policy')
    cnx = get_db()
    cursor = cnx.cursor()

    cursor.execute("UPDATE configurations SET capacity = %s, policy = %s WHERE config_id = 1",
                   (capacity_result, policy_result))
    cnx.commit()
    cnx.close()
    return redirect(url_for('success', msg="Configuration changed successfully"))


@webapp.route('/upload_form', methods=['GET'])
def upload_form():
    """Display an empty HTML form that allows users to define upload new key image pair"""
    return render_template("upload_form.html")


@webapp.route('/upload', methods=['POST'])
def upload():
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
                "code": 400,
                "message": "No image file or key given"
            }}
        return redirect(url_for('failure', msg="No image file or key given or they are not given through form"))

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_id = %s'''

    cursor.execute(has_key, (image_key,))

    folder = webapp.config['UPLOAD_FOLDER']
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
            name, extension = os.path.splitext(filename)
            filename = name + str(count) + extension
        while os.path.isfile(filename):
            count = count + 1
            name, extension = os.path.splitext(filename)
            filename = name[:-1] + str(count) + extension
        image_file.save(filename)
        query = ''' INSERT INTO images (image_id, image_path) VALUES (%s,%s)'''
        cursor.execute(query, (image_key, filename))
        cnx.commit()

    cnx.close()
    key_image[image_key] = filename

    return redirect(url_for('success', msg="Image Successfully Uploaded"))
