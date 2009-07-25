import models.core as core


def loadViews(file="views.js"):
  views = open(file).read()
  pass


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
