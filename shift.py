from couchdb.client import Server
import time

# define a decorator to make the function call

def create(data):
  """
  Create a shift.
  """
  server = Server("http://localhost:5984/")
  db = server["python-test"]

  now = time.time()
  data["type"] = "shift"
  data["created"] = now
  
  db.create(data)


def delete(data):
  # don't delete the stream, user doesn't own it
  server = Server("http://localhost:5984/")
  db = server["python-test"]


def update(data):
  pass

  
