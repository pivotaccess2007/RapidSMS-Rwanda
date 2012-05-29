from django.core.management.base import BaseCommand
from django.conf import settings
import urllib2
import time
import datetime
from reporters.models import *

class Smser(BaseCommand):
	help = "To send SMS"

	backend = PersistantBackend.objects.get(title="kannel")
	
	def send_message(self, identity, message):
		connection = PersistantConnection(backend = self.backend,identity = identity)
		#conf = {'kannel_host':'127.0.0.1', 'kannel_port':13013, 'kannel_password':'kannel', 'kannel_username':'kannel'}
		
		try:
			conf = settings.RAPIDSMS_CONF["kannel"]
		
			url = "http://%s:%s/cgi-bin/sendsms?to=%s&text=%s&password=%s&user=%s" % (
			    conf["kannel_host"], 
			    conf["kannel_port"],
			    urllib2.quote(connection.identity.strip()), 
			    urllib2.quote(message),
			    conf['kannel_password'],
			    conf['kannel_username'])

			f = urllib2.urlopen(url, timeout=10)
			if f.getcode() / 100 != 2:
			    print "Error delivering message to URL: %s" % url
			    raise RuntimeError("Got bad response from router: %d" % f.getcode())

			# do things at a reasonable pace
			time.sleep(.2)
			return True
		except KeyError:
			return settings.RAPIDSMS_APPS["kannel"]
	
	

