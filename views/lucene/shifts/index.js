function(doc)
{
  if(doc.type == 'shift')
  {
    var ret = new Document();
    ret.add(doc.href, {field:"href"});
    ret.add(doc.href.substr(7, doc.href.length).split("/")[0], {field:"domain"});
    ret.add(doc.publishData.streams.join(" "), {field:"streams"});
    ret.add(doc.publishData['private'], {field:"private"});
    ret.add(doc.publishData.draft, {field:"draft"});
    ret.add(new Date(doc.modified), {field:"modified"});
    return ret;
  }
  return null;
}