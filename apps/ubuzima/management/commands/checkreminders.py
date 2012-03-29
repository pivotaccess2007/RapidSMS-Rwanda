
from django.core.management.base import BaseCommand
from ubuzima.models import Report, Reminder, ReminderType
from django.conf import settings
from reporters.models import Reporter
import urllib2
import time
import datetime
from optparse import make_option

class Command(BaseCommand):
    help = "Checks and triggers all reminders.  This command should be run daily via cron"
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry',
                    action='store_true',
                    dest='dry',
                    default=False,
                    help='Executes a dry run, doesnt send messages or update the db.'),
        )

    def send_message(self, connection, message):
        conf = {'kannel_host':'127.0.0.1', 'kannel_port':13013, 'kannel_password':'kannel', 'kannel_username':'kannel'}
        try:
            conf = settings.RAPIDSMS_APPS["kannel"]
        except KeyError:
            pass
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

    def check_reminders(self, today, days, reminder_type, to_sup=False):
        try:
            # get the matching reminders
            pending = Report.get_reports_with_edd_in(today, days, reminder_type)

            # for each one, send a reminder
            for report in pending:
                if to_sup:
                    try:
                        print "supervisors of: %s" % report.reporter.alias
    
                        # look up the supervisors for the reporter's location
                        sups = Reporter.objects.filter(location=report.reporter.location, groups__pk=2)
                        for sup in sups:
                            # determine the right messages to send for this reporter
                            message = reminder_type.message_kw
                            if sup.language == 'en':
                                message = reminder_type.message_en
                            elif sup.language == 'fr':
                                message = reminder_type.message_fr

                            message = message % report.patient.national_id

                            print "sending reminder to %s of '%s'" % (sup.connection().identity, message)

                            # and send it off
                            if not self.dry:
                                self.send_message(sup.connection(), message)
                    except Reporter.DoesNotExist:
                        pass

                else:
                    try:
                        message = reminder_type.message_kw
                        if report.reporter.language == 'en':
                            message = reminder_type.message_en
                        elif report.reporter.language == 'fr':
                            message = reminder_type.message_fr

                        message = message % report.patient.national_id

                        print "sending reminder to %s of '%s'" % (report.reporter.connection().identity, message)
                        if not self.dry:
                            self.send_message(report.reporter.connection(), message)
                    except Reporter.DoesNotExist:
                        pass

                if not self.dry:
                    report.reminders.create(type=reminder_type, date=datetime.datetime.now(), reporter=report.reporter)
        except Reporter.DoesNotExist:
            pass

    def check_expired_reporters(self):
        # get our reminder
        reminder_type = ReminderType.objects.get(pk=6)
        today = datetime.date.today()

        # get all our pending expired reporters
        for reporter in Reminder.get_expired_reporters(today):
            # look up the supervisors for this reporter
            sups = Reporter.objects.filter(location=reporter.location, groups__pk=2)
            for sup in sups:
                # determine the right messages to send for this reporter
                message = reminder_type.message_kw
                if sup.language == 'en':
                    message = reminder_type.message_en
                elif sup.language == 'fr':
                    message = reminder_type.message_fr
                    
                message = message % (reporter.alias, reporter.connection().identity)

                print "notifying %s of expired reporter with '%s'" % (sup.connection().identity, message)
                print reporter.last_seen()
                
                # and send it off
                if not self.dry:
                    self.send_message(sup.connection(), message)

            if not self.dry:
                Reminder.objects.create(type=reminder_type, date=datetime.datetime.now(), reporter=reporter)

    def handle(self, **options):
        print "Running reminders.."

        self.dry = options['dry']

        if self.dry:
            self.dry = True
            print "DRY RUN -- No messages will be sent, no database commits made."

        # today
        today = datetime.date.today()

        # ANC2
        reminder_type = ReminderType.objects.get(pk=1)
        self.check_reminders(today, Report.DAYS_ANC2, reminder_type)

        # ANC3
        reminder_type = ReminderType.objects.get(pk=2)
        self.check_reminders(today, Report.DAYS_ANC3, reminder_type)

        # ANC4
        reminder_type = ReminderType.objects.get(pk=3)
        self.check_reminders(today, Report.DAYS_ANC4, reminder_type)

        # EDD
        reminder_type = ReminderType.objects.get(pk=4)
        self.check_reminders(today, Report.DAYS_EDD, reminder_type)

        # On the due date (Revence)
        reminder_type = ReminderType.objects.get(name = 'Due Date')
        self.check_reminders(today, Report.DAYS_ON_THE_DOT, reminder_type)

        # Seven days after due date (Revence)
        reminder_type = ReminderType.objects.get(name = 'Week After Due Date')
        self.check_reminders(today, Report.DAYS_WEEK_LATER, reminder_type)

        # EDD for SUPs
        reminder_type = ReminderType.objects.get(pk=5)
        self.check_reminders(today, Report.DAYS_SUP_EDD, reminder_type, to_sup=True)

        # Finally look for any reports who need reminders
        self.check_expired_reporters()

        print "Complete."

        if self.dry:
            print "DRY RUN Complete."
