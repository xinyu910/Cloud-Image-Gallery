import base64
import os
import mysql.connector
from flask import render_template, request, g, redirect, url_for
from werkzeug.utils import secure_filename
import requests

from FrontEnd import webapp
from FrontEnd.config import db_config

UPLOAD_FOLDER = './static/images'
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.gif', '.tif', '.bmp', '.raw', '.cr2', '.nef', '.orf', '.sr2',
                      '.psd', '.xcf', '.ai', 'cdr'}


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


def allowed_file(filename):
    return '.' in filename and ('.' + filename.rsplit('.', 1)[1]) in ALLOWED_EXTENSIONS


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
    query = '''SELECT image_key, image_path
                    FROM images;
                '''
    cursor.execute(query)
    rows = cursor.fetchall()
    cnx.close()
    # does not call api post endpoint because we also want to show the file path on the html page.
    '''
        res = requests.post('http://localhost:5000/api/list_keys')
        if res.status_code == 200:
            print(res.json()['keys'])
            return render_template("key_list.html", cursor=res.json()['keys'])
        else:
            return redirect(url_for('failure', msg=res.json()['error']['message']))
    '''
    return render_template("key_list.html", cursor=rows)


@webapp.route('/retrieve_key_form', methods=['GET'])
def retrieve_key_form():
    """Display an empty HTML form that allows users to browse image by key"""
    return render_template("key_form.html")


@webapp.route('/key', methods=['POST'])
def key():
    """Display the image user browsed by key"""
    image_key = request.form.get('key')

    if image_key == '':
        return redirect(url_for('failure', msg="Key is not given or not given from form"))

    # find if this key image pair is in memcache, if so, retrieve and render it directly from cache.
    dataSend = {"key": image_key}
    res = requests.post('http://localhost:5001/GET', json=dataSend)
    if res.status_code == 200:
        return render_template('show_image.html', key=image_key, image=res.json()['content'])
    else:
        # if not in cache, get from database and call put in memcache
        cnx = get_db()
        cursor = cnx.cursor()

        # check if database has the key or not
        has_key = "SELECT image_path FROM images WHERE image_key = %s"

        cursor.execute(has_key, (image_key,))
        rows = cursor.fetchall()
        cnx.close()

        if rows:
            path = rows[0][0]
            path = path.replace('\\', '/')
            base64_image = base64.b64encode(open(path, "rb").read()).decode('utf-8')
            dataSend = {"key": image_key, "image": base64_image}
            requests.post('http://localhost:5001/PUT', json=dataSend)
            return render_template('show_image.html', key=image_key, image=base64_image)
        else:
            return redirect(url_for('failure', msg="Unknown Key"))


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
    clear_result = request.form.get('clear')

    cnx = get_db()
    cursor = cnx.cursor()

    cursor.execute("UPDATE configurations SET capacity = %s, policy = %s WHERE config_id = 1",
                   (capacity_result, policy_result))
    cnx.commit()
    cnx.close()
    dataSend = {"clear": clear_result}
    res = requests.post('http://localhost:5001/refreshConfiguration', json=dataSend)
    if res.status_code == 200:
        return redirect(url_for('success', msg="Configuration changed successfully"))
    else:
        return redirect(url_for('failure', msg="Memcache configuration error"))


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
        return redirect(url_for('failure', msg="No image file or key given or they are not given through form"))

    if not allowed_file(image_file.filename):
        return redirect(url_for('failure', msg="Image file type not supported"))

    cnx = get_db()
    cursor = cnx.cursor()

    # check if database has the key or not
    has_key = ''' SELECT image_path FROM images WHERE image_key = %s'''

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
        query = '''UPDATE images SET image_path = %s WHERE image_key = %s'''
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
        query = ''' INSERT INTO images (image_key, image_path) VALUES (%s,%s)'''
        cursor.execute(query, (image_key, filename))
        cnx.commit()

    cnx.close()

    return redirect(url_for('success', msg="Image Successfully Uploaded"))


if __name__ == '__main__':
    webapp.run(host='0.0.0.0', port=5000, debug=True)
