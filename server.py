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

    def PUT(self, data):
        return "Trying to create a user"

    def GET(self, userName):
        return "User name is %s" % userName

    def POST(self, data):
        return "Updating a user"

    def DELETE(self, userName):
        return "Trying to delete %s" % userName


class Shift:
    exposed = True

    def PUT(self, data):
        return "Trying to create a shift"

    def GET(self, id):
        return "Getting shift %s" % id

    def POST(self, data):
        return "Updating a shift"

    def DELETE(self, id):
        return "Trying to delete a shift"


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
