import couchdb.client

def connect():
  server = couchdb.client.Server("http://localhost:5984/")
  return server["shiftspace"]




