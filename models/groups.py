import core
import utils
import schema

def inGroup(id):
  """
  Returns all users in a particular group.
  """
  db = core.connect()
  options = {"key": id}
  result = []
  for row in db.view("_design/groups/_view/all", None, **options):
    row.value.update({"id":row.id})
    result.append(row.value)
  return result

