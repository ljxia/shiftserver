import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy

cherrypy.config.update({'environment': 'embedded'})

class Root(object):
    def index(self):
        return 'Hello World from CherryPy!'
    index.exposed = True

application = cherrypy.Application(Root(), None)