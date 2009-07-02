import core
import utils
import schema

def shifts(id):
  """
  Returns all shifts for a user.
  """
  db = core.connect()
  # shifts = db.view("_by_group", None, {"key":2})
  # return shifts

def feeds(id):
  pass

def feed(id, streamId):
  pass
