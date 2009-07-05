import os
import time
import cherrypy

import user
import routes
import shift
import groups
import simplejson as json


class User:
    def POST(self, data):
        return "Trying to create a user"

    def GET(self, userName):
        return json.dumps(user.get(userName))

    def PUT(self, data):
        return "Updating a user"

    def DELETE(self, userName):
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

    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              condition=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              condition=dict(method="GET"))
    # User Routes
    # Group Routes
    # Stream Routes
    # Event Routes


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes()}}


def startServer(config=None):
    cherrypy.config.update({'server.socket_port':8080})
    if config:
        cherrypy.config.update(config)
    app = cherrypy.tree.mount(root=None, config=appconf)
    cherrypy.quickstart(app, '/~davidnolen/shiftspace/shiftserver', appconf)
 
 
if __name__ == '__main__':
    startServer(os.path.join(os.path.dirname(__file__), 'server.conf'))
