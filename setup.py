import os
import models.core as core


def isJsFile(path):
  """
  Returns True or False is a path is a directory or a Javascript file.
  """
  return os.path.splitext(path)[1] == '.js'


def walk(dir, op=None):
  """
  Parse a directory for javascript files.
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


def loadViews(viewDir="views"):
  """
  Load all database views into a dictionary
  """
  designDocs = {}

  def collect(path):
    parts = path.split("/")
    designDoc = parts[1]
    print designDoc
    view = os.path.splitext(parts[2])[0]
    if not designDocs.get(designDoc):
      designDocs[designDoc] = {}
    designDocs[designDoc][view] = open(path).read()

  walk(viewDir, collect)

  return designDocs
  


def init():
  server = core.server()
  if not server.__contains__("shiftspace"):
    print "Creating shiftspace database"
    server.create("shiftspace")
  else:
    print "shiftspace database already exists"
  loadViews()


if __name__ == "__main__":
  pass
