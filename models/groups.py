import core
import utils
import schema

def inGroup(id):
  """
  Returns all users in a particular group.
  """
  db = core.connect()
  return core.query("_design/groups/_view/all", id)

