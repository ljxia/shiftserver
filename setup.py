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
  Load all database views into a dictionary
  """
  designDocs = {}

  def collect(path):
    parts = path.split("/")
    designDoc = parts[1]
    view = os.path.splitext(parts[2])[0]
    if not designDocs.get(designDoc):
      designDocs[designDoc] = {}
    designDocs[designDoc][view] = open(path).read()

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
