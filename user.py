import core
import utils
import schema


def create(data):
  """
  Create a new user.
  """
  data["joined"] = utils.isotime()
  newUser = schema.user()
  newUser.update(data)

  return db.create(newUser)



def get(id):
  """
  Returns a user.
  """
  db = core.connect()
  return db[id]


def update(data):
  """
  Update a user.
  """
  pass


def delete(id):
  """
  Delete a user.
  """
  db = core.connect()
  del db[i]


def shifts(id):
  """
  Returns all shifts for a user.
  """
  db = core.connect()
  pass


def feeds(id):
  pass


def feed(id, streamId):
  pass
