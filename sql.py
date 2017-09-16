import mysql.connector
import copy
from util.env import *

env = get_env()
if str(env['password']) != 'None':
    config = {
        'user': str(env['user']),
        'password': str(env['password']),
        'host': '127.0.0.1',
        'database': str(env['database']),
        'raise_on_warnings': False,
    }
else:
    config = {
        'user': str(env['user']),
        'host': '127.0.0.1',
        'database': str(env['database']),
        'raise_on_warnings': False,
    }


class ippDB():
    def __init__(self):
        self.config = config
        self.cnx = mysql.connector.connect(**self.config)
        self.cursor = self.cnx.cursor(dictionary=True)

    def __del__(self):
        self.cursor.close()
        self.cnx.close()


class dbFunction(ippDB):
    def __init(self):
        ippDB.__init__(self)

    def dataQuery(self, qry):
        k = 0
        self.cursor.execute(qry)
        t = []
        for i in self.cursor:
            t.append(i)
        return t

    def dataUpdate(self, insrt):
        self.cursor.execute(insrt)
        self.cnx.commit()


class userDB(dbFunction):
    def __init__(self, uid):
        dbFunction.__init__(self)
        self.uid = int(uid)
        res = self.dataQuery(("SELECT u_name, group_id FROM users WHERE id=%d" % self.uid))
        if res:
            self.group_id = int(res[0]['group_id'])
            self.u_name = res[0]['u_name']
        else:
            self.u_name = ''

    def isolateUser(self):
        return self.dataQuery(("SELECT * FROM users WHERE pid=0 AND role='stu'"))

    def validUser(self):
        if self.u_name:
            return True
        return False

    def query(self):
        return self.dataQuery(("SELECT * FROM users WHERE id = %d" % self.uid))[0]

    def newUser(self, u_name, role, phone, major, sex):
        self.u_name = u_name
        self.group_id = 0
        op = ("INSERT INTO users VALUES ('%d', '%s', '%s', %d, '%s', '%s', 'n', 0, 0, 0, 0, 0)" % (
            self.uid, u_name, role, int(phone), major, sex))
        self.dataUpdate(op)

    def deleteUser(self):
        op = ("DELETE FROM users WHERE id=%d" % self.uid)
        self.dataUpdate(op)

    def assign(self, pid):
        op = ("UPDATE users SET pid='%s' WHERE id=%d" % (pid, self.uid))
        self.dataUpdate(op)

    def unassign(self, pid):
        op = ("UPDATE users SET pid = 0 WHERE pid=%d" % pid)
        self.dataUpdate(op)

    def allStudents(self):
        return self.dataQuery(("SELECT id, u_name, grouped, group_id FROM users WHERE role = 'stu'"))

    def freeStudents(self):
        return self.dataQuery(("SELECT *  FROM users WHERE role = 'stu'"))

    def isLeader(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        return res[0]['grouped'] == "l"

    def isGrouped(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        return res[0]['grouped'] == 'n'

    def groupStat(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        return res[0]['grouped']

    def registerProject(self, order, pid, group_id=0):
        if group_id == 0:
            op = ("UPDATE users SET wish%d='%d' WHERE id=%d" % (order, pid, self.uid))
        else:
            op = ("UPDATE users SET wish%d='%d' WHERE group_id=%d" % (order, pid, group_id))
        self.dataUpdate(op)

    def quitProject(self, pid, group_id=0):
        for i in range(3):
            if group_id == 0:
                op = ("UPDATE users SET wish%d=0 WHERE wish%d=%d AND id=%d" % (i, i, pid, self.uid))
            else:
                op = ("UPDATE users SET wish%d=0 WHERE wish%d=%d AND group_id=%d" % (i, i, pid, group_id))
            self.dataUpdate(op)

    def joinGroup(self, group_id):
        leader = self.dataQuery(("SELECT * FROM users WHERE grouped='l' AND group_id=%d" % group_id))[0]
        count = self.dataQuery(("SELECT count(id) FROM users WHERE group_id=%d" % group_id))[0]['count(id)']
        if count < 4:
            op = ("UPDATE users SET grouped='y', group_id=%d, wish0='%s', wish1='%s', wish2='%s' WHERE id=%d" %
                  (group_id, leader['wish0'], leader['wish1'], leader['wish2'], self.uid))
            self.dataUpdate(op)
        # qry = self.dataQuery(("SELECT users, user_id FROM groups WHERE id=%d" % id))[0]
        # if qry['users']:
        #     users = qry['users'].split(',')
        #     ids = qry['user_id'].split(',')
        #     ids.append(str(self.uid))
        #     users.append(self.u_name)
        # else:
        #     ids = [str(self.uid)]
        #     users = [self.u_name]
        # ids = ','.join(ids)
        # users = ','.join(users)
        # op = ("UPDATE groups SET users='%s', user_id='%s' WHERE id=%d" % (users, ids, id))
        # self.dataUpdate(op)
        # op = ("UPDATE users SET group_id=%d, grouped='y' WHERE id=%d" % (id, self.uid))
        # self.dataUpdate(op)
        # leader = self.dataQuery("SELECT leader_id FROM groups WHERE id=%d" % id)[0]['leader_id']
        # res = self.dataQuery("SELECT registed FROM users WHERE id=%d" % leader)[0]['registed']
        # self.register(res)

    def quitGroup(self):
        if self.group_id > 0:
            print(self.group_id)
            if self.isLeader():
                op = ("UPDATE users SET grouped='n', group_id=0 WHERE group_id=%d" % self.group_id)
                self.dataUpdate(op)
                groupDB(self.group_id).delete()
            else:
                op = ("UPDATE users SET grouped='n', group_id=0 WHERE id=%d" % self.uid)
                self.dataUpdate(op)
                count = self.dataQuery(("SELECT count(id) FROM users WHERE group_id=%d" % self.group_id))[0][
                    'count(id)']
                if count == 0:
                    groupDB(self.group_id).delete()
        self.group_id = 0

    # def leaderQuit(self):
    #     gid = self.query()['group_id']
    #     grp = groupDB(int(gid)).members()
    #     for mem in grp:
    #         if mem:
    #             userDB(int(mem)).quitGroup()
    #     op = ("DELETE FROM groups WHERE id=%d" % gid)
    #     self.dataUpdate(op)
    #     op = ("UPDATE users SET grouped='n', group_id=0 WHERE id=%d" % self.uid)
    #     self.dataUpdate(op)
    #     wish = self.query()['registed'].split(',')
    #     for i in range(3):
    #         if wish[i] != 'n':
    #             projectDB(wish[i]).changeChosen(i + 1, -1)
    #     self.group_id = 0

    def createGroup(self):
        new_group = groupDB()
        new_group.newGroup(self)
        self.group_id = new_group.id
        self.dataUpdate(("UPDATE users SET grouped='l', group_id=%d WHERE id=%d" % (self.group_id, self.uid)))
        # qry = self.query()
        # wish = qry['registed'].split(',')
        # for i in range(3):
        #     if wish[i] != 'n':
        #         projectDB(wish[i]).changeChosen(i + 1, 1)


class groupDB(dbFunction):
    def __init__(self, id=0):
        dbFunction.__init__(self)
        if id == 0:
            max = self.dataQuery(("SELECT MAX(id) FROM groups"))[0]['MAX(id)']
            if max:
                self.id = max + 1
            else:
                self.id = 1
        else:
            self.id = int(id)

    def allGroups(self):
        return self.dataQuery(("SELECT * FROM groups"))

    def all_users(self):
        res = [self.dataQuery(("SELECT leader_id FROM groups WHERE id=%d" % self.id))[0]['leader_id']]
        for i in self.dataQuery(("SELECT user_id FROM groups WHERE id=%d" % self.id))[0]['user_id'].split(','):
            res.append(i)
        return res

    def members(self):
        qry = self.dataQuery(("SELECT user_id FROM groups WHERE id=%d" % self.id))[0]['user_id']
        res = qry.split(',')
        return res

    def leader(self):
        return self.dataQuery(("SELECT leader_id FROM groups WHERE id=%d" % self.id))[0]['leader_id']

    def leaderName(self):
        return self.dataQuery(("SELECT leader FROM groups WHERE id=%d" % self.id))[0]['leader']

    def memberName(self):
        return self.dataQuery(("SELECT users FROM groups WHERE id=%d" % self.id))[0]['users']

    def newGroup(self, user):
        max = self.dataQuery(("SELECT MAX(id) FROM groups"))[0]['MAX(id)']
        if max:
            self.id = max + 1
        else:
            self.id = 1
        op = ("INSERT INTO groups VALUES (%d, '%s', '', %d, '', '0')" % (self.id, user.u_name, user.uid))
        self.dataUpdate(op)

    def deleteMember(self, uid):
        op = ("UPDATE groups SET users")
        self.dataUpdate(op)

    def delete(self):
        op = ("DELETE FROM groups WHERE id=%d" % self.id)
        self.dataUpdate(op)


class projectDB(dbFunction):
    def __init__(self, id=0):
        dbFunction.__init__(self)
        if id == 0:
            max = self.dataQuery(("SELECT MAX(id) FROM projects"))[0]['MAX(id)']
            if max:
                self.id = max + 1
            else:
                self.id = 1
        else:
            self.id = int(id)

    def users(self):
        return self.dataQuery(("SELECT u_name FROM users WHERE pid=%d" % self.id))

    def getFiles(self):
        return self.dataQuery(("SELECT * FROM files WHERE pid=%d" % self.id))

    def allProjects(self):
        return self.dataQuery(("SELECT * FROM projects"))

    def view(self):
        viewed = int(self.query()['views']) + 1
        op = ("UPDATE projects SET views=%d WHERE id=%d" % (viewed, self.id))
        self.dataUpdate(op)

    def query(self):
        data = self.dataQuery(("SELECT * FROM projects WHERE id = %d" % self.id))
        return data and data[0] or None

    def newWish(self, userid, seq):
        qry = ("SELECT wish%d FROM projects WHERE id = %d" % (seq, self.id))
        res = self.dataQuery(qry)[0]['wish%d' % seq]
        if res:
            res += ','
            res = res + str(userid)
        else:
            res = str(userid)
        op = ("UPDATE projects SET wish%d='%s' where id=%d" % (seq, res, self.id))
        self.dataUpdate(op)
        if userDB(int(userid)).isLeader():
            self.changeChosen(int(seq), 1)

    def newProject(self, title, detail, img, sponsor='', instructor='', major='', files='[]'):
        op = (
            "INSERT INTO projects VALUES (%d, '%s', '%s', '%s', '%s', '', '', '', 0, 0, 0, 0, 0, '%s', '%s', 'n')" % (
                self.id, title, img, sponsor, detail, major, instructor))
        self.dataUpdate(op)
        return self.id

    def deleteProject(self):
        qry = self.query()
        for i in range(1, 4):
            users = qry['wish' + str(i)]
            users = users.split(',')
            for user in users:
                if user == '':
                    break
                db = userDB(user)
                if db.groupStat() != 'y':
                    continue
                if not db.validUser():
                    db = userDB(groupDB(user).leader())
                registed = db.query()['registed'].split(',')
                registed[i - 1] = 'n'
                db.register(','.join(registed))
        op = ("DELETE FROM projects WHERE id=%d" % self.id)
        self.dataUpdate(op)

    def changeChosen(self, seq, change):
        qry = self.query()
        chosen = int(qry['chosen_num%d' % seq])
        op = ("UPDATE projects SET chosen_num%d=%d WHERE id=%d" % (seq, chosen + int(change), self.id))
        self.dataUpdate(op)

    def editProject(self, title, detail, img, sponsor, instructor, major, files='[]'):
        if img:
            op = (
                "UPDATE projects SET title='%s', detail='%s', img='%s', sponsor='%s', instructor='%s', major='%s' WHERE id=%d" % (
                    title, detail, img, sponsor, instructor, major, self.id))
        else:
            op = (
                "UPDATE projects SET title='%s', detail='%s', sponsor='%s', instructor='%s', major='%s' WHERE id=%d" % (
                    title, detail, sponsor, instructor, major, self.id))
        self.dataUpdate(op)

    def assigned(self, status='y'):
        op = ("UPDATE projects SET assigned='%s' WHERE id=%d" % (status, self.id))
        self.dataUpdate(op)

    def selectNum(self):
        data = []
        for i in range(3):
            num = self.dataQuery(("SELECT count(id) FROM users WHERE wish%d = %d" % (i, self.id)))[0]['count(id)']
            group_num = \
                self.dataQuery(("SELECT count(id) FROM users WHERE wish%d = %d AND grouped = 'l'" % (i, self.id)))[0][
                    'count(id)']
            data.append([num, group_num])
        return data

    def assignedUser(self):
        return self.dataQuery(("SELECT * FROM users WHERE pid='%d'" % self.id))


class fileDB(dbFunction):
    def __init__(self, id=0):
        dbFunction.__init__(self)
        if id == 0:
            max = self.dataQuery(("SELECT MAX(id) FROM files"))[0]['MAX(id)']
            if max:
                self.id = max + 1
            else:
                self.id = 1
        else:
            self.id = int(id)

    def query(self):
        return self.dataQuery(
            ("SELECT * FROM files WHERE id = %d" % self.id))[0]

    def newFile(self, pid, name, sha1, size, thumbnail=0):
        op = ("INSERT INTO files VALUES ('%d', '%d', '%s', '%s', '%d', '%d')" %
              (self.id, int(pid), name, sha1, int(size), thumbnail))
        self.dataUpdate(op)

    def deleteFile(self, sha1):
        print(sha1)
        op = ("DELETE FROM files WHERE sha1 = '%s'" % sha1)
        self.dataUpdate(op)
