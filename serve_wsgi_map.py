#!/usr/bin/env python

import sys, os, base64
import MapServer, serverutil, SimpleXMLRPCServer

class Handler:

  def _dispatch(self, request, environ):
    #print >> sys.stderr, 'Handler._dispatch called, request = [', request, ']', environ
    server = MapServer.MapServer()
    server.request = request
    server.environ = environ

    auth = environ.get('HTTP_AUTHORIZATION', None)
    if auth:
      auth = auth.split()
      if len(auth) == 2:
        if auth[0].lower() == "basic":
          server.auth = base64.b64decode(auth[1]).split(':')
          server.hash = serverutil.hash(request)
          #print >> sys.stderr, 'writing hash =', server.hash

    try:
      #request = iqserialize.unserialize(request)
      response = []
      #for methodname, params in request:
      #  response.append(server._dispatch(methodname, params))

      #handler = MapServer.CGIRequestHandler(allow_none = True)
      handler = SimpleXMLRPCServer.SimpleXMLRPCDispatcher(allow_none = True)
      handler.register_introspection_functions()
      handler.register_instance(server)
      #handler.handle_request(request_text = request)
      response = handler._marshaled_dispatch(request)

      success = True
    except Exception, e:
      response = repr(e)
      success = False

    return response # hack # iqserialize.serialize((success, response))

handler = Handler()


def application(environ, start_response):
  try:
    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  except (ValueError):
    request_body_size = 0

  if request_body_size > 300*1024*1024:
    sys.stderr.write('ignoring request of size %u MB' % (request_body_size/1024/1024))
    status = '413 Request Entity Too Large'
    response_body = 'Request is too large'

  else:
    request_body = environ['wsgi.input'].read(request_body_size)

    response_body = handler._dispatch(request_body, environ)

    status = '200 OK'


  response_headers = [('Content-Type', 'application/octet-stream'),
                      ('Content-Length', str(len(response_body)))]

  start_response(status, response_headers)
  return [response_body]

