#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import BaseHTTPServer
import random
import re
import urllib

from urlparse import urlparse, parse_qs
from datetime import datetime
from rapidsms.connection import Connection
from rapidsms.message import Message

def _uni(str):
    """
    Make inbound a unicode str
    Decoding from utf-8 if needed

    """
    try:
        return unicode(str)
    except:
        return unicode(str,'utf-8')

def _str(uni):
    """
    Make inbound a string
    Encoding to utf-8 if needed

    """
    try:
        return str(uni)
    except:
        return uni.encode('utf-8')

class RapidBaseHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''The base handler for use in the http backends.  This is a
       simple extension of the python builtin handlers with
       logging capabilities and a utility method for responding
       to incoming requiests.'''

    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_str(msg))

    
class HttpHandler(RapidBaseHttpHandler):
    '''The original http handler, used by the httptester app.
       URLS are /PhoneNumber/Message'''
    
    msg_store = {}
    
    def do_GET(self):
        # if the path is just "/" then start a new session
        # and redirect to that session's URL
        if self.path == "/":
            session_id = random.randint(100000, 999999)
            self.send_response(301)
            self.send_header("Location", "/%d/" % session_id)
            self.end_headers()
            return
        
        # if the path is of the form /integer/blah 
        # send a new message from integer with content blah
        send_regex = re.compile(r"^/(.*?)/(.*)")
        match = send_regex.match(self.path)
        if match:
            # parse the url
            parsed = urlparse(self.path)

            # use our default backend by default
            backend = self.server.backend

            # whether we are incoming or outgoing, be default we are incoming
            incoming = True

            # if there is a query string
            if parsed.query:
                # see if there is a different backend specified
                query_string = parse_qs(parsed.query)

                # if so, try to look it up
                if 'backend' in query_string:
                    backend = self.server.backend._router.get_backend(query_string['backend'][0])
                    if not backend:
                        self.send_response(404)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write("No backend with slug: %s found." % query_string['backend'][0])
                        return


                # is this actually an outgoing message?
                if 'direction' in query_string:
                    if query_string['direction'][0].lower() == 'out':
                        incoming = False

            # parse the groups out
            match = send_regex.match(parsed.path)

            # send the message
            session_id = urllib.unquote(str(match.group(1)))
            text = urllib.unquote(_str(match.group(2)))
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if HttpHandler.msg_store.has_key(session_id) and len(HttpHandler.msg_store[session_id]):
                    resp=_str("{'phone':'%s', 'message':'%s'}" % (session_id, HttpHandler.msg_store[session_id].pop(0).replace("'", r"\'")))
                    self.wfile.write(resp)
                return
            
            # get time
            received = datetime.utcnow()
            # leave Naive!
            # received.replace(tzinfo=pytz.utc)
            c = Connection(backend, session_id)
            msg = Message(connection=c, 
                          text=text,
                          date=received)              

            # inny or outy?
            if incoming:
                backend.route(msg)
            else:
                backend._router.outgoing(msg)

            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_str("{'phone':'%s', 'message':'%s'}" % (session_id, urllib.unquote(text).replace("'", r"\'"))))
            return
            
        return
        
    def do_POST(self):
        # TODO move the actual sending over to here
        return
    
    @classmethod
    def outgoing(klass, msg):
        '''Used to send outgoing messages through this interface.'''
        #self.log_message("http outgoing message: %s" % message)
        # the default http backend just stores outgoing messages in
        # a store and provides access to them via the JSON/AJAX 
        # interface
        if HttpHandler.msg_store.has_key(msg.connection.identity):
            HttpHandler.msg_store[msg.connection.identity].append(_str(msg.text))
        else:
            HttpHandler.msg_store[msg.connection.identity] = []
            HttpHandler.msg_store[msg.connection.identity].append(_str(msg.text))
                
class MTechHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the mtech gateway, for use in Nigeria'''
    def do_GET(self):
        querystart = self.path.find("?")
        if querystart == -1:
            self.respond(500, "Must specify parameters in the URL!")
            return
        
        query_params = map((lambda t: t.split("=")), self.path[querystart + 1:].split("&"))
        
        self.accept_message(query_params)
        
        
    def do_POST(self):
        if self.rfile:
            content_len = int(self.headers["Content-Length"])
            data = self.rfile.read(content_len)
            params = map((lambda t: t.split("=")), data.split("&"))
            self.accept_message(params)
    
    def accept_message(self, params):
        # parameters are: 
        # text=message%20body
        # from=2347067277331
        # sent=200904091443.21
        # mtech_received=200904091444.48
        # operator_received=200904091444.4
        
        text = None
        sender = None
        date = None
        for key,val in params:
            if key == "text":
                # TODO watch out because urllib.unquote will blow up on unicode text 
                text = _str(text)
                text = urllib.unquote(val)
                text = _uni(text)
            elif key == "from":
                sender = val
            elif key == "sent":
                date = datetime.strptime(val, "%Y%m%d%H%M.%S")
        
        if text and sender: 
            # respond with the number and text 
            msg = self.server.backend.message(text, sender, date)
            self.server.backend.route(msg)
            self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, _str(text)))
            return
        else:
            self.respond(500, "You must specify a valid number and message")
            return

    def outgoing(self, message):
        '''An HttpHandler for the mtech gateway, for use in Nigeria'''
        self.log_message("Mtech outgoing message: %s" % message)

        
def get_params(handler):
    '''Pulls the parameters from a query string and returns them in
       a dictionary'''
    querystart = handler.path.find("?")
    if querystart == -1:
        return
    return map((lambda t: t.split("=")), handler.path[querystart + 1:].split("&"))

def post_params(handler):
    '''Pulls the parameters from the body of a POST and returns them
       in a dictionary'''
    if handler.rfile:
        content_len = int(handler.headers["Content-Length"])
        data = handler.rfile.read(content_len)
        return map((lambda t: t.split("=")), data.split("&"))
