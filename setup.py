import os
import md5
import models.core as core


def isJsFile(path):
  """
  Returns True or False is a path is a directory or a Javascript file.
  """
  return os.path.splitext(path)[1] == '.js'


def walk(dir, op=None):
  """
  Parse a directory for view files.
  """
  files = os.listdir(dir)
  for afile in files:
    path = os.path.join(dir, afile)
    if os.path.isdir(path):
      walk(path, op)
    elif os.path.isfile(path) and isJsFile(path):
      if op:
        op(path)
      else:
        print "dir: %s, file: %s" % (dir, path)


def collectDesignDocs(viewDir="views"):
  """
  Load all CouchDB design documents, their views, validation,
  and lucene documents into an array.
  """
  designDocs = {}

  def collect(path):
    parts = path.split("/")
    designDocName = "_design/%s" % parts[1]

    designDoc = designDocs.get(designDocName)
    if not designDoc:
      designDoc = {"_id": designDocName, "language":"javascript"}

    view = parts[2]

    if parts[1] != "validation":
      key = (parts[1] == "lucene" and "fulltext") or "views"
      if not designDoc.get(key):
        designDoc[key] = {}
      if not designDoc[key].get(view):
        designDoc[key][view] = {}
      fn = os.path.splitext(os.path.basename(path))[0]
      designDoc[key][view][fn] = open(path).read()
    else:
      view = os.path.splitext(os.path.basename(path))[0]
      designDoc[view] = open(path).read()

    print designDocName
    designDocs[designDocName] = designDoc

  walk(viewDir, collect)

  return designDocs


def md5hash(str):
    m = md5.new()
    m.update(str)
    return m.hexdigest()


adminUser = {
  "type": "user",
  "userName": "shiftspace",
  "password": md5hash("shiftspace")
  }


adminDoc = {
  "type": "system",
  "ids": ["shiftspace"]
  }


def loadDocs(db, createAdmin=True):
  """
  Load all of the initial documents for the database.
  Optional create admin user for debugging. Not recommended
  for deployment.
  """
  docs = collectDesignDocs()

  if createAdmin:
    docs["admins"] = adminDoc
    docs["shiftspace"] = adminUser

  for k, v in docs.items():
    print "Loading %s" % k
    db[k] = v
  print "Design documents loaded."


def init(dbname="shiftspace"):
  """
  Initialize the shiftspace database. Defaults to
  shiftspace for the database name.
  """
  server = core.server()
  if not server.__contains__(dbname):
    print "Creating database %s." % dbname
    server.create(dbname)
  else:
    print "%s database already exists." % dbname
  db = server[dbname]
  loadDocs(db)


if __name__ == "__main__":
  init()
