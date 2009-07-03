import os
import cherrypy
import routes
import shift
import groups
import simplejson as json


class Root:
    def index(self):
        return "ShiftSpace Server 1.0"
    index.exposed = True


class User:
    @cherrypy.expose
    def index(self):
        pass


class Shift:
    @cherrypy.expose
    def index(self):
        return "This is the shift controller"

    @cherrypy.expose
    def shift(self, id):
        return "Shift id is %s" % id


class Groups:
    @cherrypy.expose
    def index(self):
        return "This is the groups controller"

    @cherrypy.expose
    def inGroup(self, id):
        # set response to say json
        # cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(groups.inGroup(int(id)))


def setupRoutes():
    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect(None, ":action", controller=Root(), action="index")
    d.connect("shift", "shift/", controller=Shift()) # why doesn't this work
    d.connect("shift", "shift/:id", controller=Shift(), action="shift",
              conditions=dict(method=["GET"]))
    d.connect("group", "group/:id", controller=Groups(), action="inGroup",
              conditions=dict(method=["GET"]))

    dispatcher = d
    return dispatcher


# configuration, serves same purpose as server.conf file
conf = {

    '/': {
        'request.dispatch': setupRoutes()
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
    app = cherrypy.tree.mount(None, config=conf)
    cherrypy.quickstart(app)


if __name__ == '__main__':
    start(os.path.join(os.path.dirname(__file__), 'server.conf'))
