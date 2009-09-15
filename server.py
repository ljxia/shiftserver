import os
import sys
import getopt
import time
import cherrypy
from cherrypy.lib.static import serve_file
import ConfigParser
import routes
import email
import simplejson as json

from utils.utils import *
from utils.errors import *
from utils.decorators import *

from controllers.user import UserController
from controllers.shift import ShiftController
from controllers.stream import StreamController
from controllers.event import EventController
from controllers.permission import PermissionController
from controllers.group import GroupsController

class RootController:
    def read(self):
        return "ShiftSpace Server 1.0"

def initRoutes():
    d = cherrypy.dispatch.RoutesDispatcher()
    root = RootController()
    user = UserController(d)
    shift = ShiftController(d)
    stream = StreamController(d)
    event = EventController(d)
    permission = PermissionController(d)
    group = GroupsController(d)
    d.connect(name="root", route="", controller=root, action="read")
    return d

def start(conf=None):
    serverroot = os.path.dirname(os.path.abspath(__file__))
    webroot = os.path.dirname(serverroot)
    serveStaticFiles = False
    if conf == None:
        conf = open(os.path.join(serverroot, 'default.conf'))
    config = ConfigParser.ConfigParser({'webroot':webroot,
                                        'serverroot':serverroot})
    config.readfp(conf)
    d = {}
    for section in config.sections():
        for k, v in config.items(section):
            if d.get(section) == None:
                d[section] = {}
            if k == "tools.sessions.timeout":
                v = int(v)
            d[section][k] = v
    d['/']['request.dispatch'] = initRoutes()
    cherrypy.config.update({'server.socket_port':8080})
    app = cherrypy.tree.mount(root=None, script_name="/", config=d)
    cherrypy.quickstart(app)

def usage():
    print "You may only pass in a configuration file to load via the -f flag."

def parseArgs(argv):
    conf = "default.conf"
    try:
        opts, args = getopt.getopt(argv, "f:h", ["file="])
    except:
        print "Invalid flag\n"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            conf = open(arg)
    start(conf)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        parseArgs(sys.argv[1:])
    else:
        start()
