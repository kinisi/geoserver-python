#!/usr/bin/env python

from wsgiref.simple_server import make_server

if False:
  from serve_wsgi_basic import application
else:
  from serve_wsgi_map import application

httpd = make_server('162.242.218.22', 8081, application)
httpd.serve_forever()
