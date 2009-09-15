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
    stream = StreamController()
    event = EventController()
    permission = PermissionController()
    group = GroupsController()

    # Root
    d.connect(name="root", route="", controller=root, action="read")
    # Stream Routes
    d.connect(name="streamCreate", route="stream", controller=stream, action="create",
              conditions=dict(method="POST"))
    d.connect(name="streamRead", route="stream/:id", controller=stream, action="read",
              conditions=dict(method="GET"))
    d.connect(name="streamUpdate", route="stream/:id", controller=stream, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="streamDelete", route="stream/:id", controller=stream, action="delete",
              conditions=dict(method="DELETE"))

    d.connect(name="streamSubscribe", route="stream/:id/subscribe", controller=stream, action="subscribe",
              conditions=dict(method="POST"))
    d.connect(name="streamUnsubscribe", route="stream/:id/unsubscribe", controller=stream, action="unsubscribe",
              conditions=dict(method="POST"))

    d.connect(name="streamSetPermission", route="stream/:id/permission", controller=stream, action="setPermission",
              conditions=dict(method="POST"))
    d.connect(name="streamPermissions", route="stream/:id/permissions", controller=stream, action="permissions",
              conditions=dict(method="GET"))

    d.connect(name="streamEvents", route="stream/:id/events", controller=stream, action="events",
              conditions=dict(method="GET"))
    d.connect(name="streamPost", route="stream/:id/post", controller=stream, action="post",
              conditions=dict(method="POST"))

    d.connect(name="streamAdd", route="stream/:id/add/:userName", controller=stream, action="add",
              conditions=dict(method="POST"))
    d.connect(name="streamRemove", route="stream/:id/remove/:userName", controller=stream, action="remove",
              conditions=dict(method="POST"))
    # Event Routes
    d.connect(name="eventRead", route="event/:id", controller=event, action="read",
              conditions=dict(method="GET"))
    d.connect(name="eventUpdate", route="event/:id", controller=event, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="eventDelete", route="event/:id", controller=event, action="delete",
              conditions=dict(method="DELETE"))
    # Permission Routes
    d.connect(name="permissionCreate", route="permission", controller=permission, action="create",
              conditions=dict(method="POST"))
    d.connect(name="permissionRead", route="permission/:id", controller=permission, action="read",
              conditions=dict(method="GET"))
    d.connect(name="permissionUpdate", route="permission/:id", controller=permission, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="permissionDelete", route="permission/:id", controller=permission, action="read",
              conditions=dict(method="DELETE"))
    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))
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
