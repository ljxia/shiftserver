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


def initRoutes():
    shift = Shift()
    shifts = Shifts()
    group = Groups()
    user = User()

    d = cherrypy.dispatch.RoutesDispatcher()

    # Root

    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              conditions=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              conditions=dict(method="GET"))
    d.connect(name="shiftUpdate", route="shift/:id", controller=shift, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="shiftDelete", route="shift/:id", controller=shift, action="delete",
              conditions=dict(method="DELETE"))
    d.connect(name="shiftsRead", route="shifts/:username", controller=shifts, action="read",
              conditions=dict(method="GET"))

    # User Routes
    d.connect(name="userRead", route="user/:username", controller=user, action="read",
              conditions=dict(method="GET"))
    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))
    # Stream Routes
    # Event Routes
    return d


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes()}}

cherrypy.config.update({'server.socket_port':8080})
app = cherrypy.tree.mount(root=None, script_name='/~davidnolen/shiftspace/shiftserver', config=appconf)
# TODO: The following value should be read from an environment file - David 7/4/09
cherrypy.quickstart(app)
