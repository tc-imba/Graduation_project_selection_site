import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *
import os
import re
import json
from util.env import *

env = get_env()
base_url = env['domain'] and env['domain'] or 'http://localhost'
if env['port']:
    base_url += ':' + str(env['port'])


class detailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        pdb = projectDB(id)
        if not self.is_viewed(id):
            pdb.view()
        proj = pdb.query()
        proj['detail'] = proj['detail'].split('\n')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        res = userDB(uid).query()
        isIn = res['wish0'] == int(id) or res['wish1'] == int(id) or res['wish2'] == int(id)
        role = res['role']
        files = projectDB(int(id)).getFiles()
        num = pdb.selectNum()
        for file in files:
            file['url'] = base_url + '/file/' + file['sha1']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role,
                    baseurl=base_url, files=files, num=num, grouped=res['grouped'], nav='project')


class registerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):  # The register page
        new = self.get_argument("item")  # the new project to be chosen
        new = new.split(",")
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        self.render("register.html", new=new, role=role, nav='project')

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
            pdb = projectDB(int(res))
            pdata = pdb.query()
            if pref < 0 or pref > 2:
                self.finish('error: pref')
            if not pdata:
                self.finish('error: project not found')
            user.registerProject(pref, int(res), data['group_id'])
            self.write('success')


class quitHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        id = int(self.get_argument("id"))
        user = userDB(uid)
        data = user.query()
        if data['grouped'] == 'y':
            self.write('You need to ask team leader to quit the project')
        else:
            user.quitProject(id, data['group_id'])
            self.write("success")


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
                        isedit=isedit, pid=pid, baseurl=base_url, files=files, nav='project')

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


class assignHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = projectDB().allProjects()
        all_usr = []

        projects = {}
        for proj in projs:
            if proj['assigned'] == 'y':
                users = projectDB(proj['id']).users()
                proj['users'] = []
                for user in users:
                    proj['users'].append(user['u_name'])
            proj['wish'] = [[], [], []]
            projects[proj['id']] = proj

        free_students = userDB(uid).freeStudents()
        students = []
        groups = {}
        for student in free_students:
            user = {
                'id': student['id'],
                'u_name': student['u_name']
            }
            students.append(user)
            if student['grouped'] == 'n':
                wishes = [student['wish0'], student['wish1'], student['wish2']]
                for i in range(3):
                    if wishes[i] > 0 and wishes[i] in projects:
                        projects[wishes[i]]['wish'][i].append([user])
            else:
                if student['group_id'] in groups:
                    groups[student['group_id']]['users'].append(user)
                else:
                    groups[student['group_id']] = {'users': [user]}
                if student['grouped'] == 'l':
                    groups[student['group_id']]['wish'] = [student['wish0'], student['wish1'], student['wish2']]
        for key in groups:
            wishes = groups[key]['wish']
            for i in range(3):
                if wishes[i] > 0 and wishes[i] in projects:
                    projects[wishes[i]]['wish'][i].append(groups[key]['users'])

        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('assign_projects.html', u_name=u_name, role=role, projs=projs, all_usr=all_usr,
                        students=students, projects=projects, nav='assign')

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        if role == 'stu':
            self.finish("not authorized")

        pid = self.get_argument("pid")
        pdb = projectDB(int(pid))
        pdata = pdb.query()
        if not pdata:
            self.finish('error: project not found')

        rst = self.get_argument("reset", default=0)
        if int(rst) > 0:
            userDB(uid).unassign(int(pid))
            pdb.assigned('n')
            self.finish("success")

        if pdata['assigned'] == 'y':
            self.finish('error: project assigned')

        res = self.get_argument("usr_list")

        if not res or not pid:
            self.finish('fail')

        users = []
        uid_filter = re.compile(r'.+-(\d+)')
        for usr in res.split(','):
            uid_str = uid_filter.match(usr).group(1)
            uid = int(uid_str)
            udata = userDB(uid).query()
            if udata['pid'] != 0 or udata['role'] != 'stu':
                self.finish('error: ' + udata['id'] + ' assigned')
            users.append(udata)

        if len(users) == 0:
            self.finish('error: no user selected')

        for udata in users:
            userDB(udata['id']).assign(pid)
        pdb.assigned('y')

        self.finish('success')
