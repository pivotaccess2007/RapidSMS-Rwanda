#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import copy

from rapidsms.connection import Connection
from rapidsms.person import Person
from datetime import datetime
from rapidsms import utils


class StatusCodes:
    '''Enum for representing status types of a message or response.'''
    NONE = "None" # we don't know.  the default
    OK  = "Ok" # is great success!
    APP_ERROR = "Application Error" # application specific errors - e.g. bad data 
    GENERIC_ERROR = "Generic error" # generic errors - e.g. a catch all responder
    
    
class Message(object):
    def __init__(self, connection=None, text=None, person=None, date=None):
        if connection == None and person == None:
            raise Exception("Message __init__() must take one of: connection, person")
        self._connection = connection
        self.text = text
        self.date = ( datetime.utcnow() if date is None
                      else utils.to_naive_utc_dt(date) )
        self.person = person
        self.responses = []
        self.status = StatusCodes.NONE
        
        # a message is considered "unprocessed" until
        # rapidsms has dispatched it to all apps, and
        # flushed the responses out
        self.processed = False
    
    def __unicode__(self):
        return self.text

    @property
    def connection(self):
        # connection is read-only, since it's an
        # immutable property of this object
        if self._connection is not None:
            return self._connection
        else:
            return self.person.connection

    @property
    def peer (self):
        # return the identity (e.g. phone number) of
        # the other end of this message's connection
        return self.connection.identity 
    
    def send(self):
        """Send this message via self.connection.backend, returning
           True if the message was sent successfully."""
        return self.connection.backend.router.outgoing(self)

    def flush_responses (self):
        """Sends all responses added to this message (via the
           Message.respond method) in the order which they were
           added, and clears self.responses"""

        # keep on iterating until all of
        # the messages have been sent
        while self.responses:
            self.responses.pop(0).send()

    def error(self, text, level):
        """Apps send error messages here rather than through respond
           so users only receive one - the with the highest level of specificity"""
        #TODO implement this
        pass

    def respond(self, text, status = StatusCodes.NONE):
        """Send the given text back to the original caller of this
           message on the same route that it came in on"""
        if self.connection:
            response = self.get_response(text, status)
            self.responses.append(response)
            return True
        else: 
            return False

    def get_response(self, text, status):
        response = copy.copy(self)
        response.text = text
        response.status = status
        return response
            
    def forward (self, identity, text=None):
        if self.connection:
            target = self.connection.fork(identity)
            if text is None: text = self.text
            message = type(self)(connection=target, text=text)
            self.responses.append(message)
            return True
        else:
            return False


class EmailMessage(Message):
    """Email version of a message object, with some extra stuff that can 
       be consumed by email backends/apps."""

    def __init__(self, connection=None, text=None, person=None, date=None, 
                 subject=None, mime_type="text/plain"):
        super(EmailMessage, self).__init__(connection=connection, text=text,
                                           person=person, date=date)
        self.subject = subject
        self.mime_type = mime_type
        
    def get_response(self, text, status):
        response = Message.get_response(self, text, status)
        response.subject = "re: %s" % self.subject
        return response
    