import core
import utils
import schema

"""Some Examples.

shift.create({"content":{"foo":"bar"}})

shift.create({
  "createdBy": "1",
  "space": "Notes",
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

def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  data["created"] = utils.isotime()
  newShift = schema.shift()
  newShift.update(data)

  return db.create(newShift)


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

  id = data.id
  doc = db[id]
  doc.update(data)
  
  db[id] = doc

  return doc


def forUser(userId):
  """
  Return all the shifts for a particular user
  """
  pass
  
