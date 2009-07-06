import core
import utils
import schema


def create(data):
  """
  Create a new user.
  """
  db = core.connect()

  data["joined"] = utils.utctime()
  newUser = schema.user()
  newUser.update(data)

  return db.create(newUser)


def get(userName):
  """
  Returns public data for a user.
  """
  theUser = getFull(userName)
  
  if theUser:
    del theUser["email"]
    del theUser["groups"]
    del theUser["following"]
    del theUser["password"]
  
  return theUser


def getFull(userName):
  """
  Return the full data for a user.
  """
  theUser = core.single("_design/users/_view/byname", userName)

  if theUser:
    del theUser["type"]

  return theUser


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
  data["modified"] = utils.utctime()
  return core.update(data)


def delete(id):
  """
  Delete a user.
  """
  db = core.connect()
  # TODO: delete all events, shifts as well - not streams
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
