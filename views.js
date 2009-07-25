// design: groups
// -----------------------------------------------------------------------------

// view: all
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

// design: users
// -----------------------------------------------------------------------------

// view: all
function (doc)
{
  if(doc.type == "all")
  {
    emit(doc._id, doc);
  }
}


// view: by_name
function(doc)
{
  if(doc.type == "user")
  {
    emit(doc.userName, doc);
  }
}

// view: join_shifts
function(doc)
{
  if(doc.type == "user")
  {
    emit([doc._id, 0], doc);
  }
  else if(doc.type == "shift")
  {
    emit([doc.createdBy, 1], doc);
  }
}

// view: notify
function(doc)
{
  if(doc.type == "user")
  {
    for(var i = 0; i < doc.notify.length; i++)
    {
      emit(doc.notify[i], doc._id);
    }
  }
}


// design: shifts
// -----------------------------------------------------------------------------

// view: all
function (doc) {
  if(doc.type == "shift")
  {
    emit(doc._id, doc);
  }
}

// view: by_user
function(doc)
{
  if(doc.type == "shift")
  {
    emit(doc.createdBy, doc);
  }
}

// view: by_href
function(doc)
{
  if(doc.type == "shift")
  {
    emit(doc.href, doc);
  }
}

// view: by_domain
function (doc)
{
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit("http://"+parts[0], doc);
  }
}

// view: by_stream
function (doc)
{
  if(doc.type == "shift")
  {
    var streams = doc.publishData.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit(streams[i], doc);
    }
  }
}

// view: by_user_and_domain
function (doc)
{
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit([doc.createdBy, "http://"+parts[0]], doc);
  }
}


// design: streams
// -----------------------------------------------------------------------------

// view: all
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc._id, doc);
  }
}

// view: subscribers
function (doc)
{
  if(doc.type == "user")
  {
    var streams = doc.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit(streams[i], doc);
    }
  }
}

// view: by_object_ref
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.objectRef, doc);
  }
}

// view: by_unique_name
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.uniqueName, doc);
  }
}

// view: comments
function (doc)
{
  if(doc.type == "stream" &&
     doc.meta == "comments")
  {
    var parts = doc.objectRef.split(":");
    if(parts[0] == "shift") emit(parts[1], doc);
  }
}

// view: stream_with_events
function (doc)
{
  if(doc.type == "user")
  {
    streams = doc.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit([stream[i], 0]);
    }
  }
  else if(doc.type == "event")
  {
    emit([doc.streamId, 1]);
  }
}

// view: by_creator
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.createdBy, doc)
  }
}

// desing: events
// -----------------------------------------------------------------------------

// view: all
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc._id, doc);
  }
}

// view: by_stream
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc.streamId, doc);
  }
  if(doc.type == "shift")
  {
    for(var i = 0; i < doc.publishData.streams.length; i++)
    {
      emit(doc.publishData.streams[i], doc);
    }
  }
}

// view: by_user
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc.createdBy, doc);
  }
}


// design: permissions
// -----------------------------------------------------------------------------

// view: all
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc._id, doc);
  }
}

// view: by_user
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc.userId, doc);
  }
}

// view: by_user_and_stream
function (doc)
{
  if(doc.type == "permission")
  {
    emit([doc.userId, doc.streamId], doc);
  }
}

// view: by_stream
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc.streamId, doc);
  }
}

// validation
// -----------------------------------------------------------------------------

function(newDoc, oldDoc, userCtx)
{
  if(newDoc &&
     newDoc.type &&
     oldDoc)
  {
    if(newDoc.type != oldDoc.type)
    {
      throw {changing_type: 'Document cannot change type. ' + newDoc.type + ' -> ' + oldDoc.type};
    }
    if(newDoc.createdBy && (newDoc.createdBy != oldDoc.createdBy))
    {
      throw {changing_owner: 'You cannot change the owner of the document.'};
    }
    if(newDoc.created && (newDoc.created != oldDoc.created))
    {
      throw {changing_created: 'You cannot change the created field of the document.'};
    }
    if(newDoc.uniqueName && (newDoc.uniqueName != oldDoc.uniqueName))
    {
      throw {changing_unique_name: 'You cannot change the uniqueName field of a document.'};
    }
    if(newDoc.type == 'event')
    {
      if(newDoc.objectRef != oldDoc.objectRef)
      {
	throw {changing_objectref: 'You cannot change the objectRef of an event.'};
      }
      if(newDoc.streamId != oldDoc.streamId)
      {
	throw {rehost_event: 'You cannot rehost an event to another stream.'};
      }
    }
    if(newDoc.type == 'shift')
    {
      if(newDoc.space.name != oldDoc.space.name)
      {
	throw {changing_space: 'You cannot change the space of a shift.'};
      }
      if(newDoc.href != oldDoc.href)
      {
	throw {changing_href: 'You cannot change the url of a shift.'};
      }
      if(newDoc.domain != oldDoc.domain)
      {
	throw {changing_domain: 'You cannot change the domain of a shift.'};
      }
    }
  }
}
