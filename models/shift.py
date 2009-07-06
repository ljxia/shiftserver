import utils
import core
import stream
import schema
import permission

"""Some Examples.

shift.create({"content":{"foo":"bar"}})

shift.create({
  "createdBy": "1",
  "space": {"name": "Notes", "version": 0.1},
  "summary": "My note.",
  "content": {
    "position": {"x": 100, "y": 150},
    "size": {"x": 200, "y": 200},
    "pinRef": None,
    "filters": {"text":"html", "summary":"html"},
    "text": "A note that I think is very cool!"
  }
})
"""

def ref(id):
  return "shift:"+id


def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  theTime = utils.isotime()
  data["created"] = theTime

  newShift = schema.shift()
  newShift.update(data)
  
  shiftId = db.create(newShift)
  newShift = db[shiftId]

  # update shift with stream data
  streamId = stream.create({
      "objectRef":ref(shiftId),
      "createdBy":newShift["createdBy"],
      "created":theTime,
      "private":newShift["publishData"]["private"]
  })
  
  shiftStream = db[streamId]
  newShift['streams'] = [streamId]

  db[shiftId] = newShift

  return shiftId


def get(id):
  """
  Get a specific shift.
  """
  db = core.connect()
  return db[id]


def delete(id):
  """
  Delete a shift from the database.
  """
  db = core.connect()
  del db[id]


def update(data):
  """
  Update a shift in the database.
  """
  db = core.connect()

  id = data["id"]
  doc = db[id]
  doc.update(data)
  doc["modified"] = utils.isotime()
  
  db[id] = doc

  return doc


def byUserName(userName):
  """
  Return the list of shifts a user has created.
  """
  db = core.connect()

  options = {"key": userName}
  
  # TODO: find a better way to handle this - David 7/3/09
  for row in db.view("_design/users/_view/byname", None, **options):
    options = {"key": row.value["_id"]}
    result = []
    for row in db.view("_design/shifts/_view/byuser", **options):
      row.value.update({"id":row.id})
      result.append(row.value)
    return result


def userCanReadShift(userId, shiftId):
  db = core.connect()

  theShift = db[shiftId]

  if theShift["createdBy"] == userId:
    return True

  theUser = db[userId]

  if not theShift["publishData"]["private"]:
    return True

  streams = stream.streamsForObjectRef(ref(shiftId))
  streamIds = [astream["_id"] for astream in streams]

  perms = permission.permissionsForUser(userId)
  permStreamIds = [aperm["streamId"] for aperm in perms if aperm["level"] >= 1]

  allowed = set(streamIds).intersection(set(permStreamIds))

  if len(allowed) > 0:
    return True
