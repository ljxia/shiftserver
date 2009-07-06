// =============================================================================
// groups
// =============================================================================

// all
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    var groups = doc.groups;
    for(var i = 0; i < groups.length; i++)
    {
      emit(groups[i], doc);
    }
  }
}

// =============================================================================
// users
// =============================================================================

// byname
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    emit(doc.userName, doc);
  }
}

// =============================================================================
// shifts
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "shift")
  {
    emit(doc._id, doc);
  }
}

// byuser
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "shift")
  {
    emit(doc.createdBy, doc);
  }
}

// byhref
// -----------------------------------------------------------------------------
function(doc) {
  if(doc.type == "shift")
  {
    emit(doc.href, doc);
  }
}

// bydomain
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit("http://"+parts[0], doc);
  }
}

// byuser_and_domain
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit([doc.createdBy, "http://"+parts[0]], doc);
  }
}

// =============================================================================
// streams
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "stream")
  {
    emit(doc._id, doc);
  }
}

// byobjectref
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "stream")
  {
    emit(doc.objectRef, doc);
  }
}

// =============================================================================
// permissions
// =============================================================================

// byuser
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "permission")
  {
    emit(doc.userId, doc);
  }
}