#!/usr/bin/env python

import web
import json
import Thread
import Lock
import time
from subprocess import call
from YJJam import Jam
from YJPlaylist import Playlist

urls = (
        '/add', 'add',
        '/delete', 'delete',
        '/clear' 'clear'
        )

# web.config.debug=False
     
def initializePlaylist():
    global playlist
    playlist = Playlist()

initializePlaylist()

class add:
    def GET(self):
        token = web.input(token=None)
        print token

        if len(token) == 0:
            raise.badrequest()
        else:
            Pl
            web.header('Content-Type', 'application/json')
            return token


class delete:
    def GET(self):
        token = web.input(token=None)
        print token

        if 

# class add:
#     def GET(self):
#         state = None
#         if GPIO.input(17):
#             state = { 'state' : 'on' }
#         else:
#             state = { 'state' : 'off' }
        
#         web.header('Content-Type', 'application/json')
#         print 'Reply:', state
#         return json.dumps(state)

# class delete:
#     def GET(self):
#         query = web.input(direction=None)
#         print query
#         if query.direction == 'on':
#             GPIO.output(17,1)
#         elif query.direction == 'off':
#             GPIO.output(17,0)
#         else:
#             web.badrequest()
        
#         web.header('Content-Type', 'application/json')
#         switch = { 'switch' : query.direction }
#         print 'Reply:', switch
#         return json.dumps(switch)

if __name__ == "__main__":

    jam1 = Jam("kEX-nllC9bk")

    global playlist
    playlist.addJam(jam1)
    playlist.printJams()

     
#    app = web.application(urls, globals())
#    app.run()

#http://10.0.1.42:4242/state
#http://10.0.1.42:4242/switch?direction=on
#http://10.0.1.42:4242/switch?direction=off
#http://73.162.24.185:4242/switch?direction=off
