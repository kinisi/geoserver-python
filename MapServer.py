#!/usr/bin/env python

import sys, os, time, subprocess, json, fcntl, re, SimpleXMLRPCServer, traceback, threading, socket, collections
import datetime
import map_db

from serverutil import hash, sign

class MapServer:

  auth = None
  db = None
  db_upd2 = None

  def __init__(self):
    try:
      self.connect()
    except:
      pass

  def connect(self):
    try:
      self.db, self.db_upd2 = map_db.connect()
      #self.db = db.db
    except Exception, e:
      print >> sys.stderr, 'Error connecting to db', str(e)
      pass

  def _dispatch(self, method, params):

    userToKey = {'iphone': 'iphone-kinisi$vCDxwwG'}

    #print >> sys.stderr, "_dispatch called"
    if self.auth:
      #print >> sys.stderr, "Auth: ", self.auth
      user = self.auth[0]
      if user not in userToKey:
        raise Exception('Signature invalid')
      digest = sign(userToKey[user], self.hash)
      #print >> sys.stderr, 'our hash:', self.hash
      #print >> sys.stderr, 'our digest: ', digest, 'sent digest: ', self.auth[1]
      if digest != self.auth[1]: 
        raise Exception('Signature invalid')
      self.user = user
    else:
      self.user = None

    if method.startswith('_'):
      raise Exception('method error %s' % method)

    func = getattr(self, method)
    if func is None:
      raise Exception('method error %s' % method)

    #print >> sys.stderr, "_dispatch: Calling method %s" % method

    try:
      return func(*params)
    except Exception, e:
      print >> sys.stderr, traceback.format_exc()
      raise Exception(traceback.format_exc())

  def echo(self, message):
    return 'Echoing: %s' % message

  def get_static_data(self):
    lat = 29.651725000
    lon = -82.352250000
    r = []
    for i in range(20):
      r.append([lat-i*0.001, lon+i*0.001])
    return r

  def get_all_by_deviceid(self, deviceid):
    if not self.db:
      return None
    cur = self.db.cursor()
    cur.execute("""SELECT latitude,longitude FROM device_location WHERE device_id = %s""", (deviceid,))
    rows = cur.fetchall()
    return list(rows)

  def insert_loc(self, deviceid, lat, lon, time)
    if not self.db_upd2:
      return None
    # convert ISO8601 time format into datetime
    conv_time = datetime.datetime.strptime(today.value, "%Y%m%dT%H:%M:%S")
    cur = self.db.cursor()
    try:
      cur.execute("""INSERT INTO device_location_upd2 (db_update,device_id,timestamp,latitude,longitude) VALUES (Now(),%s,%s,%f,%f)""",(deviceid,time,conv_time.strftime('%Y-%m-%d %H:%M:%S'),lat,lon))
      db.commit()
    except:
      db.rollback()
      return False
    #cur.execute("""SELECT latitude,longitude FROM device_location_upd2 WHERE device_id = %s""", (deviceid,))
    return True


class CGIRequestHandler(SimpleXMLRPCServer.CGIXMLRPCRequestHandler):
  def handle_request(self, request_text = None):
      """Handle a single XML-RPC request passed through a CGI post method.

      If no XML data is given then it is read from stdin. The resulting
      XML-RPC response is printed to stdout along with the correct HTTP
      headers.
      """

      if request_text is None and \
          os.environ.get('REQUEST_METHOD', None) == 'GET':
          self.handle_get()
      else:
          # POST data is normally available through stdin
          try:
              length = int(os.environ.get('CONTENT_LENGTH', None))
          except (TypeError, ValueError):
              length = -1
          if length > 300*1024*1024:
              sys.stderr.write('ignoring request of size %u MB\n' % (length/1024/1024))
              return
          if request_text is None:
              request_text = sys.stdin.read(length)

          self.handle_xmlrpc(request_text)

# From http://www.acooke.org/cute/BasicHTTPA0.html
from SimpleXMLRPCServer import SimpleXMLRPCServer, \
  SimpleXMLRPCRequestHandler

class VerifyingServer(SimpleXMLRPCServer):

  def __init__(self, *args, **kargs):
    # we use an inner class so that we can call out to the
    # authenticate method
    class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
      # this is the method we must override
      def parse_request(myself):
        # first, call the original implementation which returns
        # True if all OK so far
        if SimpleXMLRPCRequestHandler.parse_request(myself):
          # next we authenticate
          #print >> sys.stderr, 'myself.request = [', myself.request, ']'
          #print >> sys.stderr, 'myself = [', myself.__dict__, ']'
          if self.authenticate(myself.headers):
            return True
          else:
            # if authentication fails, tell the client
            myself.send_error(401, 'Authentication failed')
        return False
    # and intialise the superclass with the above
    SimpleXMLRPCServer.__init__(self,
      requestHandler=VerifyingRequestHandler,
      *args, **kargs)

  def authenticate(self, headers):
    from base64 import b64decode
    #print >> sys.stderr, 'Authorization: ', headers.get('Authorization')
    (basic, _, encoded) = \
      headers.get('Authorization').partition(' ')
    #print >> sys.stderr, 'basic, encoded: ', basic, encoded
    assert basic == 'Basic', 'Only basic authentication supported'
    (username, _, password) = b64decode(encoded).partition(':')
    #print >> sys.stderr, 'username, password', username, password
    assert username == 'iphone'
    #print >> sys.stderr, 'headers: ', headers
    assert password == 'bar'

if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1]:
    #print >> sys.stderr, 'argv: [', sys.argv, ']'
    port = int(sys.argv[1])

    # Standalone case

    # Restrict to a particular path.
    #class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    class RequestHandler(SimpleXMLRPCRequestHandler):
      rpc_paths = ('/',)

    # Create server
    #server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port), requestHandler = RequestHandler, allow_none = True)
    #server = VerifyingServer(("localhost", port), requestHandler = RequestHandler, allow_none = True)
    server = VerifyingServer(("localhost", port), allow_none = True)
    server.register_introspection_functions()
    server.register_instance(MapServer())

    # Run the server's main loop
    server.serve_forever()


  else:
    if True: # CGI -- serverless
      handler = CGIRequestHandler(allow_none = True)
      handler.register_introspection_functions()
      handler.register_instance(MapServer())
      handler.handle_request()
    else:     # CGI - as a server
      #from http.server import HTTPServer
      #from http.server import CGIHTTPRequestHandler
      import BaseHTTPServer

      port = 8080
      host = '127.0.0.1'
      server_address = (host,port) 
      httpd = BaseHTTPServer.HTTPServer(server_address,CGIRequestHandler)
      print("Starting my web server on port "+str(port))
      httpd.serve_forever()

