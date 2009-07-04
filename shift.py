import core
import utils
import schema

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

def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  data["created"] = utils.isotime()
  newShift = schema.shift()
  newShift.update(data)

  return db.create(newShift)


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
