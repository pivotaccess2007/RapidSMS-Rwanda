#   RapidSMS back-end for Cristal SMPP Gateway

from __future__ import with_statement
from cristalpy import *
import datetime
import rapidsms
from rapidsms.message import Message
from rapidsms.connection import Connection
import thread

class Backend(rapidsms.backends.Backend):
    def configure(self, cristalhost = 'localhost', cristalport = 55555,
                        keyword = 'always_gets', password = '*', number = None):
        self.cristalhost = cristalhost
        self.cristalport = cristalport
        self.keyword     = keyword
        self.password    = password
        self.number      = number
        self.cristal     = None
        self._slug       = '_cristal'
        self._type       = 'CRISTAL'
        self.server.backend = self
    
    def run (self):
        with CristalConn(cristalhost = self.cristalhost,
                         cristalport = self.cristalport,
                         keyword     = self.keyword,
                         password    = self.password,
                         number      = self.number) as c:
            self.cristal = c
            thread.start_new_thread(self.to_router, c)
            while self.running:
                if self.message_waiting:
                    msg = self.next_message()
                    c.send_message(msg.connection.identity, msg.text)
            self.info("Shutting down...")
            self.server.disconnect()

    def to_router(self, c):
        while True:
            msg = c.message()
            self.server.backend.message(msg['from'],
                                        msg['message'],
                                        datetime.utcnow())
