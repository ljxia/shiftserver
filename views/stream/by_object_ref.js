function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.objectRef, doc);
  }
}