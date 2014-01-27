#!/usr/bin/python
import MySQLdb

db = None
db_upd2 = None

def connect():
  global db
  db = MySQLdb.connect(host="localhost", # your host, usually localhost
  #                     user="tcarlson", # your username
  #                      passwd="KCkApAG7Db9tnGcS", # your password
  user = 'kuser0',
  passwd = '9aad1067f476ba',
  db="kdev0") # name of the data base

  global db_upd2
  db_upd2 = MySQLdb.connect(host="localhost", # your host, usually localhost
                       user="tcarlson", # your username
                        passwd="KCkApAG7Db9tnGcS", # your password
  #user = 'kuser0',
  #passwd = '9aad1067f476ba',
  db="kdev0") # name of the data base

  return (db, db_upd2)


if __name__ == '__main__':

  connect()

  # you must create a Cursor object. It will let
  #  you execute all the query you need
  cur = db.cursor() 

  # Use all the SQL you like
  cur.execute("SELECT * FROM device_location")

  # print all the first cell of all the rows
  for row in cur.fetchall() :
      print row[0]
