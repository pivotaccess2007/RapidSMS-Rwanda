from django.db import models
from apps.reporters.models import *
from apps.locations.models import *

class AmbulanceDriver(models.Model):
    phonenumber = models.CharField(max_length = 20)
    name 	    = models.CharField(max_length = 100)
    identity    = models.CharField(max_length = 20)
    car      	= None	#	Initialised with Ambulance
    location	= models.ForeignKey(Location, related_name = 'driver_location')

    def send_notification(self, message, report):
        '''Assume that the report that came in message is scary, and needs ambulance attention _aussit^ot_. It notifies supervisors about the registration numbers of the ambulance (self) being dispatched, and tells the ambulance driver(s) about the case, the reporting CHW's number, and the location.'''

        hwmsg  = 'An ambulance driver (%s) has been notified.' % (str(self.phonenumber))
        drvmsg = 'Umujyanama w\'ubuzima ukoresha telephoni %s yohereje ubutumwa ku kigo nderabuzima cya %s ko ashobora kuba akeneneye ubufasha bwa ambilansi.' % (str(report.reporter.connection().identity), str(report.location.name))
        #   message.respond(hwmsg)
        #   for sup in Reporter.objects.filter(location = message.reporter.location, groups = ReporterGroup.objects.get(title = 'Supervisor')):
        #       message.forward(sup.connection().identity,
        #               hwmsg + ' ' + ('In response to a report "%s ..." by %s.' %
        #                               (message.text[0:7],
        #                               report.reporter.connection().identity)))
        message.forward(self.phonenumber, drvmsg)
        return hwmsg

    def __unicode__(self):
			return u'%s (%s): %s' % (str(self.name), str(self.identity), str(self.phonenumber))

class Ambulance(models.Model):
    '''Record an ambulance, drivers' numbers, and the location where it is found. That way, ambulance dispatches can be done well.'''

    drivers = models.ForeignKey(AmbulanceDriver, related_name = 'conducteur')
    plates  = models.CharField(max_length = 10)
    station = models.ForeignKey(Location, related_name = 'ambulance_station')

    def __unicode__(self):
        return '%s (%s) @ %s' % (str(self.plates), str(self.plates[0]), str(self.station))

    def __int__(self):
        return self.id
