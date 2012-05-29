from django.core.management.base import BaseCommand
from ubuzima.models import Report, Reminder, ReminderType, TriggeredAlert
from django.conf import settings
from reporters.models import Reporter
import urllib2
import time
import datetime
from optparse import make_option
from ubuzima.smser import *

class Command(BaseCommand):
    help = "Schedules.  This command should be run every 15 minutes via cron, this time can be reduced up to every minute or five but we prefer 15 minutes"
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry',
                    action='store_true',
                    dest='dry',
                    default=False,
                    help='Executes a dry run, doesnt send messages or update the db.'),
        )

    def check_unresponded_amb_alerts(self):
    	try:
	    	today = datetime.date.today()#test datetime.date(2012, 4, 12)
	    	pending = TriggeredAlert.objects.filter(date__year = today.year, date__month = today.month, date__day = today.day,\
				trigger__destination = "AMB", date__lte = datetime.datetime.now() - datetime.timedelta(hours = 2), response__in = ['','NR'])
	    	reminder_type = ReminderType.objects.get(name = "Ambulance Response")
	    	message = reminder_type.message_kw
    		
	    	for alert in pending:
	    		try:
				if alert.reporter.language == 'en':	message = reminder_type.message_en
				elif alert.reporter.language == 'fr':	message = reminder_type.message_fr
				message = message % (alert.report.patient.national_id)
    				
				print "sending reminder to %s of '%s'" % (alert.reporter.connection().identity, message)
				if not self.dry:	Smser().send_message(alert.reporter.connection().identity, message)
	    		except:	continue
	    		if not self.dry:	Reminder.objects.create(type=reminder_type, date=datetime.datetime.now(), reporter=alert.reporter)
    	except :	pass 
    
    def handle(self, **options):
        print "Running Schedules..."
    	self.dry = options['dry']

        if self.dry:
            self.dry = True
            print "DRY RUN -- No messages will be sent, no database commits made."

    	# We need to send reminders every two hours after a red alert was send, to ask whether the ambulance did com or not
    	self.check_unresponded_amb_alerts()

   	print "Schedules complete."

        if self.dry:
            print "DRY RUN Complete."
