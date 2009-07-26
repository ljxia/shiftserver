function (doc)
{
  if(doc.type == "all")
  {
    emit(doc._id, doc);
  }
}