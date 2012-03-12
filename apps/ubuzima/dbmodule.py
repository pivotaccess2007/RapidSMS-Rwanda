from django.core import management
from django.db import connection
from ubuzima.models import *
from locations.models import *
 
cursor = connection.cursor()

def loc_short_deletion():
	table='ubuzima_locationshorthand'
	try:
		cursor.execute("drop table %s" % table)
	except Exception,e:
		raise e
		#pass
	return True
	
def hc_loc_short_creation():
	management.call_command('syncdb')
	hc=Location.objects.filter(type__in=[LocationType.objects.get(name='Health Centre'),LocationType.objects.get(name='Hospital')])
	hc=hc.exclude(id__in = [int(x.original.id) for x in LocationShorthand.objects.all()])
	anc,dst,prv,loc=[],None,None,None
	for hece in hc:
		anc,dst,prv,loc=[],None,None,None
		anc=Location.ancestors(hece)
		for an in anc:
			if an.type.name=='District': dst=an
			elif an.type.name=='Province': prv=an
		if prv is None or dst is None: return False
		loc=hece
		ls=LocationShorthand(original=loc, district=dst, province=prv)
		ls.save()
	return True
		
	 
