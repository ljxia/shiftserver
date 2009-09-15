from utils.utils import *
from utils.errors import *
from utils.decorators import *
from utils.returnTypes import *
from models import user
from models import shift
from models import stream
from models import event
from models import permission
from models import group
from resource import *


class GroupsController(ResourceController):
    def routes(self, d):
        d.connect(name="groupRead", route="group/:id", controller=self, action="read",
                  conditions=dict(method="GET"))
        return d

    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            id = loggedInUser.get("_id")
            theData['createdBy'] = id
            return data(group.create(theData))
        else:
            return error("No data for group.", NoDataError)
        pass

    @jsonencode
    def read(self, id):
        # return only public groups
        return data(groups.inGroup(int(id)))
