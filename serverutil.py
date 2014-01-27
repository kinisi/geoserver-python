#!/usr/bin/env python

import hashlib, hmac

def hash(message):
  return hashlib.sha512(message).hexdigest()
def sign(key, hash):
  return hmac.new(key, hash, hashlib.sha1).hexdigest()
