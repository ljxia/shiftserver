import core
import time

# define a decorator to make the function call

def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  now = time.time()
  data["type"] = "shift"
  data["created"] = now
  
  doc = db.create(data)
  return doc


def delete(docId):
  """
  Delete a shift from the database.
  """
  # don't delete the stream, user doesn't own it
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
  
