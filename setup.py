import os
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
  Load all CouchDB design documents, their views, and validation
  documents into an array.
  """
  designDocs = {}

  def collect(path):
    parts = path.split("/")
    designDocName = "_design/%s" % parts[1]

    designDoc = designDocs.get(designDocName)
    if not designDoc:
      designDoc = {"_id":designDocName, "language":"javascript"}

    view = parts[2]

    if parts[1] != "validation":
      if not designDoc.get("views"):
        designDoc["views"] = {}
      if not designDoc["views"].get(view):
        designDoc["views"][view] = {}
      fn = os.path.splitext(os.path.basename(path))[0]
      designDoc["views"][view][fn] = open(path).read()
    else:
      view = os.path.splitext(os.path.basename(path))[0]
      designDoc[view] = open(path).read()

    designDocs[designDocName] = designDoc

  walk(viewDir, collect)

  return designDocs


def createDesignDoc(designDoc):
  pass
  

def init(dbname="shiftspace"):
  server = core.server()
  if not server.__contains__(dbname):
    print "Creating database %s." % dbname
    server.create(dbname)
  else:
    print "%s database already exists." % dbname
  loadViews()


if __name__ == "__main__":
  pass
