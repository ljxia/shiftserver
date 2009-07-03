import os
import cherrypy
import routes
import shift
import groups
import simplejson as json


# TODO:
# 1. Authentication
# 2. Sessions
# 3. Tool for handling response


class User:
    exposed = True

    def GET(self, userName):
        return "User name is %s" % userName


class Shift:
    exposed = True

    def GET(self, id):
        return "Shift id is %s" % id


class Shifts:
    exposed = True

    def GET(self, userName):
        return json.dumps(shift.byUserName(userName))


class Groups:
    exposed = True

    def GET(self, id):
        return json.dumps(groups.inGroup(int(id)))


class ShiftSpaceServer:
    exposed = True
    shift = Shift()
    shifts = Shifts()
    group = Groups()
    user = User()

    def GET(self):
        return "ShiftSpace Server 1.0"

"""
def setupRoutes():
    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect("", ":action", controller=Root(), action="index")
    d.connect("", "shift/", controller=Shift(), action="index") 
    d.connect(None, "shift/:id", controller=Shift(), action="shift",
              conditions=dict(method=["GET"]))
    d.connect(None, "group/:id", controller=Groups(), action="inGroup",
              conditions=dict(method=["GET"]))

    dispatcher = d
    return dispatcher
"""


# configuration, serves same purpose as server.conf file
conf = {

    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },

    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.dir': 'static'
        }

    }


# can merge configuration files
def start(config=None):
    if config:
        cherrypy.config.update(config)
    app = cherrypy.tree.mount(ShiftSpaceServer(), config=conf)
    cherrypy.quickstart(app)


if __name__ == '__main__':
    start(os.path.join(os.path.dirname(__file__), 'server.conf'))
