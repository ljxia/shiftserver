import os
import time
import cherrypy

import user
import routes
import shift
import groups
import simplejson as json


class User:
    def create(self, data):
        return "Trying to create a user"

    def read(self, userName):
        return json.dumps(user.get(userName))

    def update(self, data):
        return "Updating a user"

    def delete(self, userName):
        return "Trying to delete %s" % userName

    def query(self):
        return "Query user"

    def login(self, userName, password):
        user = self.read(userName)
        return "Login user %s" % user

    def logout(self):
        return "Logout user"


class Shift:
    def create(self):
        return shift.create(json.loads(cherrypy.request.body.read()))

    def read(self, id):
        return json.dumps(shift.get(id))

    def update(self, data):
        return "Updating a shift"

    def delete(self, id):
        return "Trying to delete a shift"


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
    d.connect(name="userRead", route="user/:userName", controller=user, action="read",
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
                 'tools.sessions.storage_path':"/Users/davidnolen/Sites/shiftserver/session",
                 'tools.sessions.timeout': 60}}

cherrypy.config.update({'server.socket_port':8080})
# TODO: The following value should be read from an environment file - David 7/4/09
app = cherrypy.tree.mount(root=None, script_name='/~davidnolen/shiftspace/shiftserver', config=appconf)
cherrypy.quickstart(app)
