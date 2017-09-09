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
from util.env import *
from PIL import Image

env = get_env()
base_url = env['domain'] and env['domain'] or 'http://localhost'
if env['port']:
    base_url += ':' + str(env['port'])


class createProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        pid = self.get_argument('id', default='')
        if pid:
            project = projectDB(int(pid)).query()
            title = project['title']
            detail = project['detail']
            isedit = "true"
        else:
            project = {'instructor': '', 'sponsor': '', 'major': ''}
            title = ''
            detail = ''
            isedit = 'false'
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('create_project.html', u_name=u_name, proj=project, role=role, title=title, detail=detail,
                        isedit=isedit, pid=pid, baseurl=base_url)

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            pic_name = self.get_secure_cookie('pic_name')
            if pic_name:
                pic_name = pic_name.decode('UTF-8')
            else:
                pic_name = ''
            isedit = self.get_argument("isedit")
            if not pic_name and isedit == "false":
                self.finish('Upload error')
            title = self.get_argument("title")
            detail = self.get_argument("detail")
            sponsor = self.get_argument("sponsor")
            instructor = self.get_argument("instructor")
            major = self.get_argument('major')
            detail = detail.replace("'", "''")
            sponsor = sponsor.replace("'", "''")
            instructor = instructor.replace("'", "''")
            major = major.replace("'", "''")
            img = pic_name
            if isedit == "false":
                projectDB().newProject(title, detail, img, sponsor, major, instructor)
            else:
                pid = self.get_argument("pid")
                projectDB(pid).editProject(title, detail, img, sponsor, instructor, major)
            self.clear_cookie("pic_name")
            self.write("success")


class quitProj(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        id = int(self.get_argument("id"))
        user = userDB(uid)
        res = user.query()
        if res['grouped'] == 'y':
            self.write('You need to ask team leader to quit the project')
        else:
            registed = res['registed'].split(',')
            if str(id) in registed:
                registed[registed.index(str(id))] = 'n'
                user.register(','.join(registed))
                self.write("success")
            else:
                self.write("You havn't registered the project")


class registerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):  # The register page
        new = self.get_argument("item")  # the new project to be chosen
        new = new.split(",")
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        self.render("register.html", new=new, role=role)

    @tornado.web.authenticated
    def post(self):  # Post the result of chosen project
        res = self.get_argument("res")
        pref = int(self.get_argument("pref"))
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        data = user.query()
        if data['grouped'] == 'y':
            self.write('You need to ask team leader to register the project')
        else:
            data = data['registed'].split(',')
            data[pref] = res
            data = ','.join(data)
            user.register(data)
            self.write('success')


class detailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        proj = projectDB(id)
        if not self.is_viewed(id):
            proj.view()
        proj = proj.query()
        for i in range(3):
            k = 0
            for mem in proj['wish%d' % (i + 1)].split(','):
                if not mem:
                    continue
                if userDB(int(mem)).isLeader():
                    k += 1
            proj['chosen_num%d' % (i + 1)] = k
        proj['detail'] = proj['detail'].split('\n')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        res = userDB(uid).query()
        isIn = id in res['registed']
        role = res['role']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role,
                    baseurl=base_url)


MIN_FILE_SIZE = 1  # 1B
MAX_FILE_SIZE = 10485760  # 10MB
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
# ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMB_MAX_WIDTH = 80
THUMB_MAX_HEIGHT = 80
THUMB_SUFFIX = '.' + str(THUMB_MAX_WIDTH) + 'x' + str(THUMB_MAX_HEIGHT) + '.png'
EXPIRATION_TIME = 300  # seconds


class uploadFileHandler(BaseHandler):
    @tornado.web.authenticated
    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        else:
            return True
        return False

    def write_blob(self, data, info):
        filename_temp = hashlib.sha1(data).hexdigest() + '.' + info['name']
        file_path = 'temp/' + filename_temp
        key = 'uploadfile?type=temp&key=' + filename_temp
        thumbnail_key = None
        file = open(file_path, 'wb')
        file.write(data)
        file.close()
        if IMAGE_TYPES.match(info['type']):
            im = Image.open(file_path)
            im.thumbnail((THUMB_MAX_WIDTH, THUMB_MAX_HEIGHT))
            im.save('temp/thumb.' + filename_temp)
            thumbnail_key = 'temp/thumb.' + filename_temp
        return key, thumbnail_key

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
                key, thumbnail_key = self.write_blob(file.body, result)
                if key is not None:
                    result['url'] = base_url + '/' + key
                    result['deleteUrl'] = result['url']
                    result['deleteType'] = 'DELETE'
                    if thumbnail_key is not None:
                        result['thumbnailUrl'] = base_url + '/' + thumbnail_key
                else:
                    result['error'] = 'Failed to store uploaded file.'
            results.append(result)
        return results

    def head(self):
        pass

    def get(self):
        self.redirect(base_url)

    def delete(self):
        key = self.get_argument('key')
        _type = self.get_argument('type')
        try:
            os.remove(_type + '/' + key)
            os.remove(_type + '/thumb.' + key)
        except FileNotFoundError:
            pass
        result = {'key': key}
        s = json.dumps(result)
        self.set_header('Content-Type', 'application/json')
        self.write(s)

    def post(self):
        result = {'files': self.handle_upload()}
        s = json.dumps(result)
        self.set_header('Content-Type', 'application/json')
        self.write(s)


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


class deleteProjHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            pid = int(self.get_argument('id'))
            proj = projectDB(pid)
            proj.deleteProject()
            self.write('success')


class assignProjHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = projectDB().allProjects()
        alu = userDB(uid).allUsers()
        all_usr = []
        for usr in alu:
            user = userDB(int(usr['id']))
            if not user.isAssigned() and user.query()['role'] != 'admin':
                all_usr.append(usr)
        for proj in projs:
            proj['all'] = []
            for i in range(3):
                grp = []
                indiv = []
                stus = proj['wish' + str(i + 1)].split(',')
                for member in stus:
                    if not member:
                        continue
                    inf = userDB(int(member)).query()
                    if inf['grouped'] == 'n':
                        indiv.append(inf['u_name'])
                        proj['all'].append(inf['u_name'] + '-' + str(member))
                    elif inf['grouped'] == 'y':
                        tmp = groupDB(int(inf['group_id'])).all_users()
                        tp = []
                        for usr in tmp:
                            uname = userDB(int(usr)).query()['u_name']
                            tp.append(uname)
                            proj['all'].append(uname + '-' + str(usr))
                        grp.append(','.join(tp))
                proj['grpwish' + str(i + 1)] = grp
                proj['indivwish' + str(i + 1)] = indiv

        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('assign_projects.html', u_name=u_name, role=role, projs=projs, all_usr=all_usr)

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        if role == 'stu':
            self.finish("not authorized")
        res = self.get_argument("usr_list")
        pid = self.get_argument("pid")
        pdb = projectDB(int(pid))
        data = pdb.query()
        for i in range(3):
            old_usrs = data['wish%d' % (i + 1)].split(',')
            for old_usr in old_usrs:
                if not old_usr:
                    continue
                udb = userDB(int(old_usr))
                udata = udb.query()
                if udata['grouped'] == 'y':
                    continue
                else:
                    quit_res = udata['registed'].replace(str(pid), 'n')
                    udb.register(quit_res)
        filter = re.compile(r'.+-(\d+)')
        for usr in res.split(','):
            if not usr:
                continue
            uid = int(filter.match(usr).group(1))
            usr_db = userDB(uid)
            if usr_db.isLeader():
                usr_db.leaderQuit()
            elif usr_db.isGrouped():
                usr_db.quitGroup()
            usr_db.register('%d,n,n' % int(pid))
            usr_db.verify()
        pdb.assigned()
        self.finish('success')
