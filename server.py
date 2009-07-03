import os
import cherrypy
import routes
import shift
import groups


class Root:
    def index(self):
        return "ShiftSpace Server 1.0"
    index.exposed = True


class Shift:
    def index(self):
        return "This is the shift controller"
    def shift(self, id):
        return "Shift id is %s" % id
    index.exposed = True
    shift.exposed = True


def setupRoutes():
    d = cherrypy.dispatch.RoutesDispatcher()
    d.connect("root", ":action", controller=Root())
    #d.connect("shiftIndex", "shift/:action", controller=Shift()) # why doesn't this work
    d.connect("serveShift", "shift/:id", controller=Shift(), action="shift")
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
