import core
import utils
import schema


def create(data):
  """
  Create a stream.
  """
  db = core.connect()

  data["created"] = utils.utctime()

  newStream = schema.stream()
  newStream.update(data)

  return db.create(newStream)


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


def subscribers(streamId):
  return core.query("_design/streams/_view/subscribers", streamId)


def streamsForObjectRef(objectRef):
  """
  All streams for a objectRef, where objectRef is "type:id".
  """
  return core.query("_design/streams/_view/byobjectref", objectRef)


def byUniqueName(uniqueName):
  """
  Return the stream with a unique name.
  """
  return core.single("_design/streams/_view/byuniquename", uniqueName)


