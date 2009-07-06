import os
import time
import cherrypy

import user
import routes
import shift
import groups
import simplejson as json


ack = {"data":"ok"}

# TODO: verify logged in decorator
# TODO: json.dumps decorator

class Resource:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def updateField(self, id, key, value):
        pass
    def delete(self, id):
        pass


class User:
    def join(self):
        data = json.loads(cherrypy.request.body.read())
        if not data.get("email"):
            return json.dumps({"error":"Please specify your email address."})
        userName = data.get("userName")
        if userName == None:
            return json.dumps({"error":"Please enter a user name."})
        if len(userName) < 6:
            return json.dumps({"error":"Your user name should be at least 6 characters long."})
        if not user.nameIsUnique(userName):
            return json.dumps({"error":"That user name is taken, please choose another."})
        user.create(data)
        return json.dumps(ack)

    def read(self, userName):
        theUser = user.get(userName).copy()
        if theUser.get('password'):
            del theUser['password']
        return json.dumps(theUser)

    def update(self, userName):
        loggedInUser = cherrypy.session['loggedInUser']
        if loggedInUser['userName'] == userName:
            shift.update(cherrypy.request.body.read())
            return json.dumps(ack)
        else:
            return json.dumps({"error": "Operation not permitted. You don't have permission to update this account."})

    def delete(self, userName):
        loggedInUser = cherrypy.session['loggedInUser']
        if loggedInUser['userName'] == 'userName':
            user.delete(userName)
            return json.dumps(ack)
        else:
            return json.dumps({"error": "Operation not permitted. You don't have permission to delete this account."})

    def query(self):
        loggedInUser = cherrypy.session.get('loggedInUser')
        if loggedInUser:
            return json.dumps(loggedInUser)
        else:
            return json.dumps({"message":"No logged in user"})

    def login(self, userName, password):
        theUser = user.get(userName)
        if theUser and theUser['password'] == password:
            cherrypy.session['loggedInUser'] = theUser
            return json.dumps(theUser)
        return "Error"

    def logout(self):
        loggedInUser = cherrpy.session['loggedInUser']
        if loggedInUser:
            cherrpy.session['loggedInUser'] = None
            return json.dumps({"data":"ok"})
        return json.dumps({"error":"No user logged in."})


class Shift:
    def create(self):
        loggedInUser = cherrpy.session['loggedInUser']
        if loggedInUser:
            data = json.loads(cherrypy.request.body.read())
            data['createdBy'] = loggedInUser.get("_id")
            return shift.create(data)
        else:
            return json.dumps({"error":"Operation not permitted. You are not logged in"})

    def read(self, id):
        loggedInUser = cherrpy.session['loggedInUser']
        if loggedInUser and shift.userCanReadShift(loggedInUser.get("_id"), id):
            return json.dumps(shift.get(id))
        else:
            return json.dumps({"error":"Operation not permitted. You don't have permission to view this shift."})

    def update(self, id):
        loggedInUser = cherrpy.session['loggedInUser']
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['userId']:
            shift.update(cherrpy.request.body.read())
            return json.dumps(ack)
        else:
            return json.dumps({"error":"Operation not permitted. You don't have permission to update this shift."})

    def delete(self, id):
        loggedInUser = cherrpy.session['loggedInUser']
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['userId']:
            shift.delete(id)
            return json.dumps(ack)
        else:
            return json.dumps({"error":"Operation not permitted. You don't have permission to delete this shift."})


class Event:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass


class Stream:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass


class Permission:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass


class Shifts:
    def read(self, userName):
        return json.dumps(shift.byUserName(userName))


class Groups:
    def read(self, id):
        return json.dumps(groups.inGroup(int(id)))


class Root:
    def read(self):
        return "ShiftSpace Server 1.0"


def initRoutes():
    root = Root()
    user = User()
    shift = Shift()
    shifts = Shifts()
    group = Groups()

    d = cherrypy.dispatch.RoutesDispatcher()

    # Root
    d.connect(name="root", route="", controller=root, action="read")

    # User Routes
    d.connect(name="userJoin", route="user/join", controller="user", actino="join",
              conditions=dict(method="POST"))
    d.connect(name="userLogin", route="user/login", controller=user, action="login",
              conditions=dict(method="POST"))
    d.connect(name="userLogout", route="user/logout", controller=user, action="logout",
              conditions=dict(method="POST"))
    d.connect(name="userQuery", route="user/query", controller=user, action="query",
              conditions=dict(method="GET"))
    d.connect(name="userRead", route="user/view/:userName", controller=user, action="read",
              conditions=dict(method="GET"))

    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              conditions=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              conditions=dict(method="GET"))
    d.connect(name="shiftUpdate", route="shift/:id", controller=shift, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="shiftDelete", route="shift/:id", controller=shift, action="delete",
              conditions=dict(method="DELETE"))
    d.connect(name="shiftsRead", route="shifts/:userName", controller=shifts, action="read",
              conditions=dict(method="GET"))

    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))

    # Stream Routes

    # Event Routes

    return d


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes(),
                 'tools.sessions.on': True,
                 'tools.sessions.storage_type': "file",
                 'tools.sessions.storage_path':"/Users/davidnolen/Sites/shiftserver/sessions",
                 'tools.sessions.timeout': 60}}

cherrypy.config.update({'server.socket_port':8080})
# TODO: The following value should be read from an environment file - David 7/4/09
app = cherrypy.tree.mount(root=None, script_name='/~davidnolen/shiftspace/shiftserver', config=appconf)
cherrypy.quickstart(app)
