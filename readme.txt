Dependencies
================================================================================

1. couchdb-python 0.6   
   http://pypi.python.org/packages/source/C/CouchDB/CouchDB-0.6.tar.gz
2. couchdb 0.10dev      
   svn co http://svn.apache.org/repos/asf/couchdb/trunk couchdb   
3. cherrypy 3.1.2       
   http://download.cherrypy.org/cherrypy/3.1.2/
4. routes 1.10.3        
   http://pypi.python.org/packages/source/R/Routes/Routes-1.10.3.tar.gz
5. couchdb-lucene 0.4   
   http://github.com/rnewson/couchdb-lucene/tree/master
6. Apache2
7. mod_wsgi

Installation
================================================================================

You can setup the server code in one of two ways. Proxying the built in
cherrypy web server to Apache, or using mod_wsgi. Proxying works well
for development enviroment. mod_wsgi is the way to go for
deployments.

mod_wsgi
================================================================================

proxy
================================================================================
