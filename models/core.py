import couchdb.client
import schema

def connect():
  server = couchdb.client.Server("http://localhost:5984/")
  return server["shiftspace"]


def query(view, key):
  db = connect()
  options = {"key": key}
  result = []
  for row in db.view(view, None, **options):
    result.append(row.value)
  return result


def queryRange(view, startKey, endKey):
  db = connect()
  options = {"startKey": startKey, "endKey": endKey}
  result = []
  for row in db.view(view, None, **options):
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
  schema = getattr(schema, doc.type)()
  schemaKeys = schema.keys()
  docKeys = doc.keys()
  return set(docKeys).issubset(set(schemaKeys))
