import core
import utils
import schema


def create(data):
  """
  Create a stream.
  """
  pass


def update(data):
  """
  Update a stream.
  """
  pass


def delete(id):
  """
  Delete a stream.
  """
  pass


def subscribe(id, userId):
  """
  Subscribe a user to a stream.
  """
  db = core.connect()
  
  user = db[userId]
  db[userId] = user["streams"].append(id)


def unsubscribe(id, userId):
  """
  Unsubscribe a user to a stream.
  """
  db = core.connect()

  user = db[userId]
  db[userId] = user.remove(id)


def find(uniqueName, filters):
  """
  Find a public stream with the specified unique name."
  """
  pass


def streamsForObjectRef(objectRef):
  """
  All streams for a objectRef, where objectRef is "type:id".
  """
  db = core.connect()
  options = {"key": objectRef}
  result = []
  for row in db.view("_design/streams/_view/byobjectref", None, **options):
    result.append(row.value)
  return result
