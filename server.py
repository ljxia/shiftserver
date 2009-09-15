import os
import sys
import time
import cherrypy
from cherrypy.lib.static import serve_file
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
    root = RootController()
    user = UserController()
    shift = ShiftController()
    stream = StreamController()
    event = EventController()
    permission = PermissionController()
    group = GroupsController()

    d = cherrypy.dispatch.RoutesDispatcher()

    # Root
    d.connect(name="root", route="", controller=root, action="read")
    # User Routes
    d.connect(name="userLogin", route="login", controller=user, action="login",
              conditions=dict(method="POST"))
    d.connect(name="userLogout", route="logout", controller=user, action="logout",
              conditions=dict(method="POST"))
    d.connect(name="userQuery", route="query", controller=user, action="query",
              conditions=dict(method="GET"))
    d.connect(name="userJoin", route="join", controller=user, action="join",
              conditions=dict(method="POST"))

    d.connect(name="userRead", route="user/:userName", controller=user, action="read",
              conditions=dict(method="GET"))
    d.connect(name="userUpdate", route="user/:userName", controller=user, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="userDelete", route="user/:userName", controller=user, action="delete",
              conditions=dict(method="DELETE"))

    d.connect(name="userMessages", route="user/:userName/messages", controller=user, action="messages",
              conditions=dict(method="GET"))
    d.connect(name="userFeeds", route="user/:userName/feeds", controller=user, action="feeds",
              conditions=dict(method="GET"))
    d.connect(name="userShifts", route="user/:userName/shifts", controller=user, action="shifts",
              conditions=dict(method="GET"))
    d.connect(name="userFavorites", route="user/:userName/favorites", controller=user, action="favorites",
              conditions=dict(method="GET"))
    d.connect(name="userComments", route="user/:userName/comments", controller=user, action="comments",
              conditions=dict(method="GET"))

    d.connect(name="userFollow", route="follow/:userName", controller=user, action="follow",
              conditions=dict(method="POST"))
    d.connect(name="userUnfollow", route="unfollow/:userName", controller=user, action="unfollow",
              conditions=dict(method="POST"))
    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              conditions=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              conditions=dict(method="GET"))
    d.connect(name="shiftUpdate", route="shift/:id", controller=shift, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="shiftDelete", route="shift/:id", controller=shift, action="delete",
              conditions=dict(method="DELETE"))

    d.connect(name="shiftPublish", route="shift/:id/publish", controller=shift, action="publish",
              conditions=dict(method="POST"))
    d.connect(name="shiftUnpublish", route="shift/:id/unpublish", controller=shift, action="unpublish",
              conditions=dict(method="POST"))

    d.connect(name="shiftFavorite", route="shift/:id/favorite", controller=shift, action="favorite",
              conditions=dict(method="POST"))
    d.connect(name="shiftUnfavorite", route="shift/:id/unfavorite", controller=shift, action="unfavorite",
              conditions=dict(method="POST"))

    d.connect(name="shiftComments", route="shift/:id/comments", controller=shift, action="comments",
              conditions=dict(method="GET"))
    d.connect(name="shiftComment", route="shift/:id/comment", controller=shift, action="comment",
              conditions=dict(method="POST"))

    d.connect(name="shiftNotify", route="shift/:id/notify", controller=shift, action="notify",
              conditions=dict(method="POST"))
    d.connect(name="shiftUnnotify", route="shift/:id/unnotify", controller=shift, action="unnotify",
              conditions=dict(method="POST"))

    d.connect(name="shifts", route="shifts", controller=shift, action="shifts",
              conditions=dict(method="GET"))
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

# Configure the application, sessions, and static file serving
appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes(),
                 'tools.sessions.on': True,
                 'tools.sessions.storage_type': 'file',
                 'tools.sessions.timeout': 60}}

if __name__ == '__main__':
    serverroot = os.path.dirname(os.path.abspath(__file__))
    webroot = os.path.dirname(serverroot)
    serveStaticFiles = True

    try:
        appconfigfile = open("config.json")
        appconfig = json.loads(appconfigfile.read())
        serveStaticFiles = appconfig['serve_static_files']
        appconf['/'].update({'tools.staticdir.root': appconfig['tools.staticdir.root'],
                             'tools.sessions.storage_path': appconf['tools.sessions.storage_path']})
    except Exception:
        appconf['/'].update({'tools.staticdir.root': webroot,
                             'tools.sessions.storage_path': os.path.join(serverroot, 'sessions')})

    if serveStaticFiles:
        appconf.update({'/builds':    {'tools.staticdir.on': True,
                                        'tools.staticdir.dir': 'builds'},
                        '/externals': {'tools.staticdir.on': True,
                                       'tools.staticdir.dir': 'externals'},
                        '/sandbox':   {'tools.staticdir.on': True,
                                       'tools.staticdir.dir': 'sandbox'}})

    cherrypy.config.update({'server.socket_port':8080})
    # TODO: The following value should be read from an environment file - David 7/4/09
    app = cherrypy.tree.mount(root=None, script_name="/", config=appconf)
    cherrypy.quickstart(app)
