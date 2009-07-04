import time

import cherrypy
import simplejson as json

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        yield "Wow! The current time is %s<br />" % time.ctime()
        yield "hmm %s" % json.dumps({"foo":"bar"})
        yield "A <a href='static/test.txt'>static file</a> served by Apache."

appconf = {'/': {'tools.proxy.on':True,}
       }

cherrypy.config.update({'server.socket_port':8080})
cherrypy.quickstart(HelloWorld(), '/~davidnolen/shiftspace/shiftserver', appconf)
