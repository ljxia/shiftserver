import couchdb.client
import schema


def server():
  return couchdb.client.Server("http://localhost:5984/")


def connect():
  server = couchdb.client.Server("http://localhost:5984/")
  return server["shiftspace"]


def query(view, key=None):
  db = connect()

  rows = None
  options = None

  if key:
    options = {"key": key}
    rows = db.view(view, None, **options)
  else:
    rows = db.view(view)

  result = []
  for row in rows:
    result.append(row.value)
  return result


def single(view, key):
  db = connect()
  options = {"key": key}
  for row in db.view(view, None, **options):
    return row.value


def update(doc):
  db = connect()
  id = doc["_id"]
  old = db[id]
  new = old.update(doc)
  db[id] = new
  return new


def validate(doc):
  theSchema = getattr(schema, doc["type"])()
  schemaKeys = theSchema.keys()
  docKeys = doc.keys()
  print schemaKeys
  print docKeys
  return set(docKeys).issubset(set(schemaKeys))
