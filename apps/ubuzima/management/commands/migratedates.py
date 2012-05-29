
from django.core.management.base import BaseCommand
from ubuzima.models import Report
from datetime import datetime

class Command(BaseCommand):
    help = "Migrates our old string dates to new SQL dates.  This command only needs to be run once."

    def handle(self, **options):
        # get all items which have a date_string but no date
        candidates = Report.objects.filter(date=None).exclude(date_string=None)

        print "Updating date fields.."

        # for each candidate
        for candidate in candidates:
            # see if we can parse the date, if so set our date off of it
            try:
                candidate.date = datetime.strptime(candidate.date_string, "%d.%m.%Y")
                candidate.save()
                print ".",
            except ValueError,e:
                # no-op, just keep the current value and move on
                pass            

        print "Complete."

