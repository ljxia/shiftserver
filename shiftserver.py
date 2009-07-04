import time
import cherrypy

import routes
import shift
import groups
import simplejson as json

class User:
    exposed = True

    def POST(self, data):
        return "Trying to create a user"

    def GET(self, userName):
        return "User name is %s" % userName

    def PUT(self, data):
        return "Updating a user"

    def DELETE(self, userName):
        return "Trying to delete %s" % userName


class Shift:
    exposed = True

    def POST(self, data):
        return "Trying to create a shift"

    def GET(self, id):
        return json.dumps(shift.get(id))

    def PUT(self, data):
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


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}

cherrypy.config.update({'server.socket_port':8080})

# TODO: The following value should be read from an environment file - David 7/4/09
cherrypy.quickstart(ShiftSpaceServer(), '/~davidnolen/shiftspace/shiftserver', appconf)
