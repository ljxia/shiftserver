from utils.utils import *
from utils.errors import *
from utils.decorators import *
from utils.returnTypes import *
from models import user
from models import shift
from models import stream
from models import event
from models import permission
from resource import *


class GroupsController(ResourceController):
    @jsonencode
    def read(self, id):
        # return only public groups
        return data(groups.inGroup(int(id)))
