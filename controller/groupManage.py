import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *


class joinGroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        u_name = user.u_name
        res = user.query()
        stat = res['grouped']
        gid = res['group_id']
        role = res['role']
        res = user.allStudents()

        groups = {}
        for student in res:
            if student['grouped'] != 'n':
                id = student['group_id']
                if id not in groups:
                    groups[id] = {'leader': {}, 'members': []}
                if student['grouped'] == 'l':
                    groups[id]['leader'] = {'id': student['id'], 'u_name': student['u_name']}
                else:
                    groups[id]['members'].append({'id': student['id'], 'u_name': student['u_name']})

        # print(groups)
        self.render("groups.html", stat=stat, gid=gid, users=res, u_name=u_name, groups=groups, role=role, nav='group')


    @tornado.web.authenticated
    def post(self):
        method = self.get_argument('method')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        # if user.isLeader():
        #     grp = groupDB(user.query()['group_id'])
        #     for member in grp.members():
        #         if not member:
        #             break
        #         userDB(member).quitGroup()
        #     user.leaderQuit()
        #     self.write("Success")
        #     return
        # print(method)
        # print(int(self.get_argument('gid')))
        if method == 'join':
            grp = user.query()['group_id']
            if grp:
                self.write('success')
                return
            group_id = int(self.get_argument('gid'))
            user.joinGroup(group_id)
            self.write('success')
        elif method == 'create':
            if user.query()['grouped'] == 'n':
                user.createGroup()
                self.write('success')
        else:
            user.quitGroup()
            self.write('success')
