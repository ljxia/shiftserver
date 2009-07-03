import core
import utils
import schema


def inGroup(id):
  """
  Returns all users in a particular group.
  """
  db = core.connect()

  options = {"key": id}
  theGroups = db.view("_design/groups/_view/all", None, **options)
  print theGroups
  for user in db.view("_design/groups/_view/all", None, **options):
    print user
  #for row in  db.view("_all_docs"):
  #  print row
  # return shifts
