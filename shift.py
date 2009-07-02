import core
import utils
import schema

# define a decorator to make the function call

# shift.create({"content":{"foo":"bar"}})
def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  data["type"] = "shift"
  data["created"] = utils.isotime()
  
  newShift = schema.shift()
  newShift.update(data)

  return db.create(newShift)


def delete(docId):
  """
  Delete a shift from the database.
  """
  db = core.connect()
  del db[docId]


def update(data):
  """
  Update a shift in the database.
  """
  pass


def forUser(userId):
  """
  Return all the shifts for a particular user
  """
  pass
  
