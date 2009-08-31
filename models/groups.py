import core
import schema

def inGroup(id):
  """
  Returns all users in a particular group.
  """
  db = core.connect()
  return core.query(schema.allGroups, id)

