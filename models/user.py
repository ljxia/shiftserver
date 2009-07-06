import core
import utils
import schema


def create(data):
  """
  Create a new user.
  """
  db = core.connect()

  data["joined"] = utils.isotime()
  newUser = schema.user()
  newUser.update(data)

  return db.create(newUser)


def get(userName):
  """
  Returns public data for a user.
  """
  return core.single("_design/users/_view/byname", userName)


def getFull(userName):
  """
  Return the full data for a user.
  """
  pass


def getById(id):
  """
  Get a user by document id.
  """
  db = core.connect()
  return db[id]


def idForName(userName):
  """
  Get the id for a user from the userName.
  """
  theUser = get(userName)
  return theUser["_id"]


def update(data):
  """
  Update a user document.
  """
  db = core.connect()

  data["modified"] = utils.isotime()
  db[data.get("_id")] = data
  
  return data


def delete(id):
  """
  Delete a user.
  """
  db = core.connect()
  del db[i]


def nameIsUnique(userName):
  """
  Returns True or False depending on if the name is taken.
  """
  return get(userName) == None


def feeds(id, page=0, perPage=25):
  """
  Return all events for all streams that a user is subscribed to.
  """
  db = core.connect()
  theUser = db[id]
  streams = theUser["streams"]
  pass


def feed(id, streamId):
  """
  Return all events for a single feed.
  """
  pass
