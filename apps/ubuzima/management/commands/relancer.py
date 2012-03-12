# coding=utf-8
from django.core.management.base import BaseCommand
import os, re, sys

class Command(BaseCommand):
    help = 'This is for rebooting the web part of the RapidSMS system (which is linked to Cherokee).'

    def handle(self, **args):
        moi = os.getenv('USER', os.getlogin())
        permis = 'root'
        redemarrer = None
        if moi != permis:
            sys.stderr.write(u'Mec, il faut que tu soit "%s" (et non "%s").' % (permis, moi))
            exit(1)
        cmd = "ps aux | grep rapidsms | grep runfcgi | grep -v grep"
        with os.popen(cmd) as pipe:
            for ligne in pipe:
                bywho, pid, cpu, mem, vsz, rss, tt, stat, sttm, uptm, cmd = re.split(r'\s+', ligne, 10)
                os.kill(int(pid), 9)
                redemarrer = cmd.strip()
        npid = os.fork()
        if npid:
            sys.stdout.write(u'On va continuer hors de vue, en ex\'ecutant "%s", et on finira par ^etre sous le PID %d.\n' % (redemarrer, npid))
            exit(0)
        exit(os.system(redemarrer))
