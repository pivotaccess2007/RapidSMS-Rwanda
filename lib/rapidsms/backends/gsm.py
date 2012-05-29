#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import time
import pygsm
import Queue

from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.backends import Backend
import backend
from rapidsms import log
from rapidsms import utils
from datetime import datetime

POLL_INTERVAL=2 # num secs to wait between checking for inbound texts
LOG_LEVEL_MAP = {
    'traffic':'info',
    'read':'info',
    'write':'info',
    'debug':'info',
    'warn':'warning',
    'error':'error'
}

class Backend(Backend):
    _title = "pyGSM"
    
    def _log(self, modem, msg, level):
        """
        convert GsmModem levels to levels understood by
        the rapidsms logger
        
        """
        
        logger_level = 'info'
        try:
            logger_level = LOG_LEVEL_MAP[level]
        except:
            # inbound level was bofus
            pass

        if self.modem_logger is not None:
            self.modem_logger.write(self,logger_level,msg)
        else:
            self.router.log(logger_level, msg)

    def configure(self, *args, **kwargs):
        self.modem = None
        self.modem_args = args
        
        # set max outbound text size
        if 'max_csm' in kwargs:
            self.max_csm = int(kwargs['max_csm'])
        else:
            self.max_csm = 1
        
        if self.max_csm>255:
            self.max_csm = 255
        if self.max_csm<1:
                self.max_csm = 1
                
        # make a modem log
        self.modem_logger = None
        if 'modem_log' in  kwargs:
            mlog = kwargs.pop('modem_log')
            level='info'
            if 'modem_log_level' in kwargs:
                level=kwargs.pop('modem_log_level')
            self.modem_logger = log.Logger(level=level, file=mlog, channel='pygsm')
            
        kwargs['logger'] = self._log
        self.modem_kwargs = kwargs
       
    
    def __send_sms(self, message):
        try:
            self.modem.send_sms(
                str(message.connection.identity),
                message.text)
        except ValueError, err:
            # TODO: Pass this error info on to caller!
            self.error('Error sending message: %s' % err)
        
    def run(self):
        while self._running:
            # check for new messages
            msg = self.modem.next_message(True)
            
            if msg is not None:
#                self.error("index: %s" % msg.index)
#                self._log( self.modem, "index: %s" % msg.index, "info")
            
                # we got an sms! create RapidSMS Connection and
                # Message objects, and hand it off to the router 
                c = Connection(self, msg.sender)
                
                # Try to use message sent date as timestamp
                # SOMETIMES this doesn't come over, in which
                # case use the current time
                try:
                    date=utils.to_naive_utc_dt(msg.sent)
                except:
                    date=datetime.utcnow()

                m = Message(
                            connection=c, 
                            text=msg.text,
                            date=date
                            )
                self.router.send(m)
                
                # remove the message
                if msg.index:
                    self.modem.command("AT+CMGD=%s" % msg.index)
                
            # process all outbound messages
            while True:
                try:
                    self.__send_sms(self._queue.get_nowait())
                except Queue.Empty:
                    # break out of while
                    break
                
            # poll for new messages
            # every POLL_INTERVAL seconds
            time.sleep(POLL_INTERVAL)
            self.modem.command("AT+CPMS?")
    
    def start(self):
    
        print "initting modem: %s %s" % (self.modem_args, self.modem_kwargs)
    
        self.modem = pygsm.GsmModem(
            *self.modem_args,
            **self.modem_kwargs).boot()

        # set our service center
        self.modem.service_center = "+250788110333"

        # If we got the connection, call superclass to
        # start the run loop--it just sets self._running to True
        # and calls run.
        if self.modem is not None:
            backend.Backend.start(self)

    def stop(self):
        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        backend.Backend.stop(self)

        # disconnect from modem
        if self.modem is not None:
            self.modem.disconnect()



        
