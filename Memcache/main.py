# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import datetime
from datetime import timedelta
from memcache import Stats

#global memcache dict
global memcache
memcache = {}
# config from the db
# default setting capacity in MB, replacement policy: Least Recently Used or Random Replacement
memcacheConfig = {'capacity': 400000, 'policy': 'LRU'}

# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])


app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)

"""/////////////////////////////////JUST FOR TEST/////////////////////////////////////"""
@app.route('/', methods=['POST', 'GET'])
def welcome():
    return "welcome"


@app.route('/upload', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        user_input = request.form.get("name")

        basepath = os.path.dirname(__file__)  # current path
        imagename = secure_filename(f.filename)  # file name

        join_path = os.path.join(basepath, 'static/image', imagename)

        PUT(user_input, join_path, imagename)

        return render_template('uploadok.html', userinput=user_input, file_name=join_path)
    return render_template('upload.html')


"""///////////////////////////////////FOR PUT METHOD///////////////////////////////////"""
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def getSize(image_path='./static/image/testimage.png'):
    # calc size of the folder
    size = os.path.getsize(image_path)  # In Bytes
    return size


def saveFile(f, join_path):
    f.save(join_path)  # save the file to disk
    img = cv2.imread(join_path)
    cv2.imwrite(join_path, img)

#   没试过
def saveDict(key, join_path, image_name):
    with open(join_path, 'rb') as f:
        image = f.read()
    memcache[key] = {'image_name': image_name, 'content': image, 'time': datetime.datetime.now()}


"""///////////////////////////////////FOR DELET METHOD///////////////////////////////////"""

def clearCache(base_path):
        for image in os.listdir(os.path.join(base_path, 'static/image')):
            print("Trying to delete ", image)
            for filetype in ALLOWED_EXTENSIONS:
                if image.endswith(filetype):
                    print("Deleting ", image)
                    os.remove(os.path.join(base_path, 'static/image', image))

        memcache.clear()


"""//////////////////////////////////////API METHOD///////////////////////////////////"""

def PUT(user_input, join_path, image_name):
    """
    :param user_input: key
    :param join_path: target path of the image(including local path and file name)
    :param imagename: name of the image
    :return:
        json: "success": "false",
            "error": {
                "code": servererrorcode
                "message": errormessage
                }
    """

    print("-----join path------", join_path)

    """file type error"""
    f = request.files['file']
    if not (f and allowed_file(f.filename)):
        return jsonify({"success": "false",
                        "error": {"code": 400,
                                  "message": "Error: wrong file type, expecting png, jpg, JPG, PNG, bmp"
                                  }
                        })
    """file path error"""
    if not join_path:
        print("Error: Path missing!")
        message = "Error: Path missing!"
        return jsonify({"success": "false",
                        "error": {"code": 404,
                                  "message": "Path missing"
                                  }
                        })
    """path missing error"""
    if not os.path.isfile(join_path):
        message = "Error: path is missing! " + join_path
        print(message)
        return jsonify({"success": "false",
                        "error": {"code": 404,
                                  "message": message
                                  }
                        })
    """file size larger than capacity"""
    if getSize(join_path) > memcacheConfig['capacity']:
        print("Error: File size larger than capacity allowed!")
        message = "Error: File size larger than capacity"
        return jsonify({"success": "false",
                        "error": {"code": 400,
                                  "message": message
                                  }
                        })

    """f.save(join_path)  # save the file to disk
    img = cv2.imread(join_path)
    cv2.imwrite(join_path, img)"""
    saveFile(f, join_path)
    saveDict(user_input, join_path, image_name)

    """with open(join_path, 'rb') as f:
        image = f.read()
    memcache[user_input] = {'name': image_name, 'content': image, 'time': datetime.datetime.now()}"""


#   没试过
def GET(user_input):
    if user_input:
        if user_input not in memcache.keys():
            return jsonify({
                "success": "false",
                "error": {
                    "code": 400,
                    "message": "please enter a valid key"
                }
            })
        else:
            return jsonify({"success": "true",
                            "content": memcache[user_input]['content']})
    else:
        return jsonify({
            "success": "false",
            "error": {
                "code": 400,
                "message": "please enter a key"
            }
        })

#   没试过
def CLEAR():
    clearCache(os.path.dirname(__file__))
    return jsonify({"statusCode": 200,
                    "message": "OK"})


def invalidateKey(key):
    pass


def refreshConfiguration():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
