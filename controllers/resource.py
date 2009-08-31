import cherrypy
from utils.returnTypes import *
from utils.errors import *

class Helper:
    def setLoggedInUser(self, data):
        cherrypy.session['loggedInUser'] = data

    def getLoggedInUser(self):
        return cherrypy.session.get('loggedInUser')

    def getRequestBody(self):
        return cherrypy.request.body.read()
helper = Helper()


class ResourceController:
    def primaryKey(self):
        return "id"

    def resolveSource(self, id):
        return id

    def resourceDoesNotExistString(self, id):
        return ("Resource %s does not exist" % id)

    def resourceDoesNotExistType(self):
        return ResourceDoesNotExistError
