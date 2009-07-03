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
    index.exposed = True

root = Root()
root.shift = Shift()
cherrypy.tree.mount(root)

if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'server.conf'))

