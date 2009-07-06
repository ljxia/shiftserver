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

class User:
    def create(self, data):
        return "Trying to create a user"

    def read(self, userName):
        theUser = user.get(userName).copy()
        if theUser.get('password'):
            del theUser['password']
        return json.dumps(theUser)

    def update(self, userName, data):
        loggedInUser = cherrypy.session['loggedInUser']
        if loggedInUser['userName'] == userName:
            shift.update(data)
            return json.dumps(ack)
        else:
            return json.dumps({"error": "Operation not permitted."})

    def delete(self, userName):
        loggedInUser = cherrypy.session['loggedInUser']
        if loggedInUser['userName'] == 'userName':
            user.delete(userName)
            return json.dumps(ack)
        else:
            return json.dumps({"error": "Operation not permitted."})

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
        return json.dumps({"message":"No logged in user."})


class Shift:
    def create(self):
        return shift.create(json.loads(cherrypy.request.body.read()))

    def read(self, id):
        loggedInUser = cherrpy.session['loggedInUser']
        theShift = shift.get(id)
        if shift.userCanReadShift(loggedInUser.get("_id"), theShift):
            json.dumps(theShift)
        else:
            json.dumps({"error":"Operation not permitted."})

    def update(self, id):
        return shift.update(json.loads(cherrypy.request.body.read()))

    def delete(self, id):
        return shift.delete(id)


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
    d.connect(name="userLogin", route="user/login", controller=user, action="login",
              conditions=dict(method="POST"))
    d.connect(name="userQuery", route="user/query", controller=user, action="query",
              conditions=dict(method="GET"))
    # We need to use /view here becaues we have other actions - David
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
