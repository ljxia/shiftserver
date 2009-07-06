import couchdb.client


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


def single(view, key):
  db = connect()
  options = {"key": key}
  for row in db.view(view, None, **options):
    return row.value






