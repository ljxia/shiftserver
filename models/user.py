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
  Returns a user.
  """
  db = core.connect()

  options = {"key": userName}

  for row in db.view("_design/users/_view/byname", None, **options):
    return row.value


def getFull(userName):
  pass


def getById(id):
  db = core.connect()
  return db[id]


def idForName(userName):
  theUser = get(userName)
  return theUser["_id"]


def update(data):
  """
  Update a user.
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
  return get(userName) == None


def feeds(id):
  pass


def feed(id, streamId):
  pass
