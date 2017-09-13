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


class createProjectHandler(BaseHandler):
    def get_suffix(self, name):
        pos = len(name) - name[::-1].find('.')
        return name[pos:]

    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        pid = self.get_argument('id', default='')
        if pid:
            project = projectDB(int(pid)).query()
            files = projectDB(int(pid)).getFiles()
            for file in files:
                suffix = self.get_suffix(file['name'])
                file['type'] = 'file'
                file['url'] = base_url + ('/uploadfile?type=file&sha1=%s&suffix=%s' %
                                          (file['sha1'], suffix))
                file['deleteUrl'] = file['url']
                file['deleteType'] = 'DELETE'
                if file['thumbnail']:
                    file['thumbnailUrl'] = base_url + ('/file/%s.thumb.%s' % (file['sha1'], suffix))
            files = json.dumps(files)
            title = project['title']
            detail = project['detail']
            isedit = "true"
        else:
            project = {'instructor': '', 'sponsor': '', 'major': ''}
            files = '[]'
            title = ''
            detail = ''
            isedit = 'false'
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('create_project.html', u_name=u_name, proj=project, role=role, title=title, detail=detail,
                        isedit=isedit, pid=pid, baseurl=base_url, files=files)

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
                pid = projectDB().newProject(title, detail, img, sponsor, instructor, major)
            else:
                pid = self.get_argument("pid")
                projectDB(pid).editProject(title, detail, img, sponsor, instructor, major)

            files = self.get_argument('files', default='[]')
            files = json.loads(files)

            for file in files:
                try:
                    size = os.path.getsize('temp/' + file['sha1'])
                    os.rename('temp/' + file['sha1'], 'file/' + file['sha1'])
                except FileNotFoundError:
                    print(file)
                    continue
                try:
                    suffix = self.get_suffix(file['name'])
                    os.rename('temp/' + file['sha1'] + '.thumb.' + suffix,
                              'file/' + file['sha1'] + '.thumb.' + suffix)
                    thumbnail = 1
                except FileNotFoundError:
                    thumbnail = 0
                fileDB().newFile(pid, file['name'], file['sha1'], size, thumbnail)

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
        files = projectDB(int(id)).getFiles()
        for file in files:
            file['url'] = base_url + '/file/' + file['sha1']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role,
                    baseurl=base_url, files=files)


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
        print(projs)
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

        projects = projectDB().allProjects()
        assigned_students = []
        for project in projects:
            if project['assigned_students'] and project['assigned'] == 'y':
                assigned_students += project['assigned_students'].split(',')

        # print(assigned_students)

        new_students = []
        uid_filter = re.compile(r'.+-(\d+)')
        if res:
            for usr in res.split(','):
                uid_str = uid_filter.match(usr).group(1)
                uid = int(uid_str)
                print(uid_str)
                try:
                    pos = assigned_students.index(uid_str)
                    self.finish('fail')
                except ValueError:
                    # baocuo
                    new_students.append(uid)

        print(new_students)

        for student in new_students:
            udb = userDB(student)
            


        # pdb = projectDB(int(pid))
        # data = pdb.query()
        # for i in range(3):
        #     old_usrs = data['wish%d' % (i + 1)].split(',')
        #     for old_usr in old_usrs:
        #         if not old_usr:
        #             continue
        #         udb = userDB(int(old_usr))
        #         udata = udb.query()
        #         if udata['grouped'] == 'y':
        #             continue
        #         else:
        #             quit_res = udata['registed'].replace(str(pid), 'n')
        #             udb.register(quit_res)
        # filter = re.compile(r'.+-(\d+)')
        # for usr in res.split(','):
        #     if not usr:
        #         continue
        #     uid = int(filter.match(usr).group(1))
        #     usr_db = userDB(uid)
        #     if usr_db.isLeader():
        #         usr_db.leaderQuit()
        #     elif usr_db.isGrouped():
        #         usr_db.quitGroup()
        #     usr_db.register('%d,n,n' % int(pid))
        #     usr_db.verify()
        # pdb.assigned()

        self.finish('success')
