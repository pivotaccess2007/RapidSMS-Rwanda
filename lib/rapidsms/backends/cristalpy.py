#   Python interface to the Cristal SMPP Gateway
import re
import socket
import Queue
import thread

class CristalException(Exception):
    pass

class CristalConn:
    def __init__(self, cristalhost = 'localhost',
                       cristalport = 55555,
                       keyword     = 'always_gets',
                       password    = '',
                       number      = None):
        self.cristalhost = cristalhost
        self.cristalport = int(cristalport)
        self.keyword     = keyword
        self.password    = password
        self.number      = number
        self.outbox      = None
        if not self.number:
            raise CristalException, 'No sender number?'

    def __enter__(self):
        return self.start()

    def __exit__(self, _, __, ___):
        self.finish()
        return False

    def start(self):
        sck = socket.socket()
        sck.connect((self.cristalhost, self.cristalport))
        sck.sendall('{"facility":"login", "params":{"keyword":"%s", \
"pwdscheme":"pwd", "password":"%s"}}\n' % (self.keyword.replace('"', '\\"'),
                                         self.password.replace('"', '\\"')))
        fch = sck.makefile()
        if not re.match('.*proceed.*', fch.readline()):
            raise CristalException, 'Could not log in.'
        self.socket = fch
        return self

    def finish(self):
        self.socket.write('{"facility":"logout"}\n')
        self.socket.close()

    def send_message(self, dest, msg, sender = None, other_recipients = []):
        if not self.outbox:
            self.outbox = Queue()
            self.sender = thread.start_new_thread(self.keep_sending,
                                                  self.outbox)
        self.outbox.put((dest, msg, sender))

    def keep_sending(self, kyu):
        while not self.socket.closed:
            dst, txt, sdr = kyu.get()
            self.__unsafe_send_message(dst, txt, sdr)

    def __unsafe_send_message(self, dest, msg, sender = None,
                     other_recipients = []):
        sender = sender if sender else self.number
        other_recipients.append(dest)
        allrecips = ', '.join(['"%s"' % (str(x),) for x in other_recipients])
        self.socket.write('{"facility":"send", "params":{"from":"%s", "to":[%s], "message":"%s"}}\n' % (sender.replace('"', '\\"'), allrecips, msg.replace('"', '\\"')))
        self.write.flush()

    #   Insecure, but who cares? Besides, Py has no standard JSON lib.
    def message(self):
        return eval(self.socket.readline())['params']
