import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *
import time
import os
import re
import urllib.parse
import hashlib
import json
import random
from util.env import *
from PIL import Image

env = get_env()
base_url = env['domain'] and env['domain'] or 'http://localhost'
if env['port']:
    base_url += ':' + str(env['port'])

MIN_FILE_SIZE = 1  # 1B
MAX_FILE_SIZE = 10485760  # 10MB
IMAGE_TYPES = re.compile('image/(gif|bmp|p?jpeg|(x-)?png)')
# ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMB_MAX_WIDTH = 80
THUMB_MAX_HEIGHT = 80
THUMB_SUFFIX = '.' + str(THUMB_MAX_WIDTH) + 'x' + str(THUMB_MAX_HEIGHT) + '.png'
EXPIRATION_TIME = 300  # seconds


class uploadFileHandler(BaseHandler):
    @tornado.web.authenticated
    def get_suffix(self, name):
        pos = len(name) - name[::-1].find('.')
        return name[pos:]

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        else:
            return True
        return False

    def write_blob(self, data, info):
        sha1 = hashlib.sha1(data).hexdigest()
        sha1 = hashlib.sha1((sha1 + str(random.random())).encode('utf8')).hexdigest()
        # filename_temp = hashlib.sha1(data).hexdigest() + '.' + info['name']
        file_path = 'temp/' + sha1
        suffix = self.get_suffix(info['name'])
        key = 'uploadfile?type=temp&sha1=%s&suffix=%s' % (sha1, suffix)
        thumbnail_name = None
        file = open(file_path, 'wb')
        file.write(data)
        file.close()
        if IMAGE_TYPES.match(info['type']):
            im = Image.open(file_path)
            im.thumbnail((THUMB_MAX_WIDTH, THUMB_MAX_HEIGHT))
            thumbnail_name = 'temp/' + sha1 + '.thumb.' + suffix
            im.save(thumbnail_name)
        return sha1, key, thumbnail_name,

    def handle_upload(self):
        results = []
        for name in self.request.files:
            file = self.request.files[name][0]
            result = {
                'name': file.filename,
                'type': file.content_type,
                'size': len(file.body)
            }
            if self.validate(result):
                sha1, key, thumbnail_name = self.write_blob(file.body, result)
                if key is not None:
                    result['sha1'] = sha1
                    result['type'] = 'temp'
                    result['url'] = base_url + '/' + key
                    result['deleteUrl'] = result['url']
                    result['deleteType'] = 'DELETE'
                    if thumbnail_name is not None:
                        result['thumbnailUrl'] = base_url + '/' + thumbnail_name
                else:
                    result['error'] = 'Failed to store uploaded file.'
            results.append(result)
        return results

    def head(self):
        pass

    def get(self):
        sha1 = self.get_argument('sha1', default='')
        _type = self.get_argument('type', default='temp')
        filename = _type + '/' + sha1
        with open(filename, 'rb') as f:
            while True:
                data = f.read()
                if not data:
                    break
                self.write(data)
        self.finish()

    def delete(self):
        sha1 = self.get_argument('sha1', default='')
        suffix = self.get_argument('suffix', default='png')
        _type = self.get_argument('type', default='temp')
        try:
            os.remove(_type + '/' + sha1)
            os.remove(_type + '/' + sha1 + '.thumb.' + suffix)
        except FileNotFoundError:
            pass
        fileDB().deleteFile(sha1)
        result = {'key': sha1}
        s = json.dumps(result)
        self.set_header('Content-Type', 'application/json')
        self.write(s)
        self.finish()

    def post(self):
        result = {'files': self.handle_upload()}
        s = json.dumps(result)
        self.set_header('Content-Type', 'application/json')
        self.write(s)
        self.finish()


class uploadPicHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            if self.request.files:
                myfile = self.request.files['myfile'][0]
                postfix = ''
                fname = myfile['filename']
                if fname.find('.') > -1:
                    postfix = fname.split('.')[-1]
                fileName = str(time.time()) + '.' + postfix
                absPath = os.path.dirname(os.path.abspath("img"))
                fin = open(absPath + "/img/" + fileName, "wb")
                fin.write(myfile["body"])
                fin.close()
            self.set_secure_cookie("pic_name", fileName)
            self.finish(fileName)