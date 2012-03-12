from rapidsms.tests.scripted import TestScript
from app import App
from apps.reporters.app import App as ReporterApp
from django.test import TestCase

import datetime

from apps.reporters.models import Reporter, PersistantBackend, PersistantConnection
from apps.locations.models import Location
from ubuzima.models import Patient, Report, ReportType, Reminder, ReminderType, TriggeredText, FieldType

class TestUbuzima(TestCase):
    fixtures = ("fosa_location_types", "fosa_test_locations", "groups", "reporting", "reminder_types" )

    def testCalculateEDD(self):
        # simple case first
        date = datetime.date(2010, 1, 1)
        edd = Report.calculate_edd(date)
        self.assertEquals(2010, edd.year)
        self.assertEquals(10, edd.month)
        self.assertEquals(8, edd.day)

        # assert the opposite
        menses = Report.calculate_last_menses(edd)
        self.assertEquals(2010, menses.year)
        self.assertEquals(1, menses.month)
        self.assertEquals(1, menses.day)

        # now one that rolls over
        date = datetime.date(2010, 5, 28)
        edd = Report.calculate_edd(date)
        self.assertEquals(2011, edd.year)
        self.assertEquals(3, edd.month)
        self.assertEquals(4, edd.day)

        # assert the opposite
        menses = Report.calculate_last_menses(edd)
        self.assertEquals(2010, menses.year)
        self.assertEquals(5, menses.month)
        self.assertEquals(28, menses.day)

    def testCalculateReminderRange(self):
        # the edd reminder must happen one week before EDD, we bracket our 
        # query by 2 days in each direction to make sure to catch any stragglers.

        # let's say today is november 8th
        today = datetime.date(2010, 11, 8)

        # so we want to remind people who are going to deliver on the 15th
        edd = datetime.date(2010, 11, 15)

        # so those people had a last menses of Feb 8th
        menses = datetime.date(2010, 2, 8)

        (start, end) = Report.calculate_reminder_range(today, 7)

        # two days before menses
        self.assertEquals(2010, start.year)
        self.assertEquals(2, start.month)
        self.assertEquals(6, start.day)

        # two days after menses
        self.assertEquals(2010, end.year)
        self.assertEquals(2, end.month)
        self.assertEquals(10, end.day)

    def testEDDReminder(self):
        # our location
        location = Location.objects.get(code="F01001")

        # create a reporter
        reporter = Reporter.objects.create(first_name="Laurence", last_name="Lessig")

        # create a test patient
        patient = Patient.objects.create(location=location, national_id="101")

        # pregnancy type
        report_type = ReportType.objects.get(pk=4)

        # and a pregnancy report
        report = Report.objects.create(reporter=reporter, location=location,
                                       patient=patient, type=report_type)

        # our proxy current date
        today = datetime.date(2010, 11, 8)

        # the menses we will use, these people will deliver on the 15th
        last_menses = datetime.date(2010, 2, 8)

        date_string = "%02d.%02d.%d" % (last_menses.day, last_menses.month, last_menses.year)
        report.set_date_string(date_string)
        report.save()

        # our EDD reminder type
        edd_reminder = ReminderType.objects.get(pk=4)

        # get all the reports which need reminders now, which haven't already had an EDD
        # reminder
        reports = Report.get_reports_with_edd_in(today, 7, edd_reminder)

        self.assertEquals(1, len(reports))
        self.assertEquals(report.pk, reports[0].pk)

        # now insert a reminder for this report
        report.reminders.create(type=edd_reminder, date=datetime.datetime.now(), reporter=reporter)

        # and check that there are no pending reminders now
        reports = Report.get_reports_with_edd_in(today, 7, edd_reminder)
        self.assertEquals(0, len(reports))


    def testReporterReminders(self):
        # backend for our connection
        backend = PersistantBackend.objects.create(slug='reindeer', title='santas sleigh')

        # create a reporter
        reporter = Reporter.objects.create(alias='santa')
        connection = reporter.connections.create(identity='northpole', backend=backend)

        now = datetime.datetime.now()

        # set our last seen to now
        connection.last_seen = now
        connection.save()

        # test that we have no expired reporters
        expired = Reminder.get_expired_reporters(now)

        # should be no expired just yet
        self.assertEquals(0, len(expired))

        # now change our last seen to 31 days ago
        connection.last_seen = now - datetime.timedelta(31)
        connection.save()

        # we should have one expired reporter
        expired = Reminder.get_expired_reporters(now)
        self.assertEquals(1, len(expired))

        # now mark that we've reminded this reporter
        expired_type = ReminderType.objects.get(pk=6)
        reminder = Reminder.objects.create(reporter=reporter, date=datetime.datetime.now(), type=expired_type)

        # make sure we no longer trigger a reminder
        expired = Reminder.get_expired_reporters(now)
        self.assertEquals(0, len(expired))

        # finally, move the reminder so that it happened before the last time we
        # were seen, meaning it doesn't apply to this expiration
        reminder.date = connection.last_seen - datetime.timedelta(10)
        reminder.save()

        # we should need a reminder again
        expired = Reminder.get_expired_reporters(now)
        self.assertEquals(1, len(expired))

    def testTriggeredTexts(self):
        # create a reporter
        reporter = Reporter.objects.create(alias='santa')
        
        # test location
        location = Location.objects.get(code="F01001")

        # test patient
        patient = Patient.objects.create(location=location, national_id="1337")

        # pregnancy report type
        pregnancy_type = ReportType.objects.get(pk=4)
        
        # and a test report (birth for example)
        report = Report.objects.create(reporter=reporter, location=location, patient=patient, type=pregnancy_type)

        # no fields, so this shouldn't have any triggers at all
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(0, len(triggers))

        he_type = FieldType.objects.get(key='he')
        
        # ok add a trigger now, for he
        he_trigger = TriggeredText.objects.create(name="HE Advice", description="Desc",
                                                  message_kw="foo", message_fr="le foo", message_en="yo foo",
                                                  destination='CHW')
        he_trigger.triggers.add(he_type)

        # make sure we still don't trigger
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(0, len(triggers))

        # now add a value to the report with this field type
        report.fields.create(type=he_type)

        # now we should trigger
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(1, len(triggers))
        self.assertEquals(he_trigger.pk, triggers[0].pk)

        mc_type = FieldType.objects.get(key='mc')

        # add another trigger which shouldn't get triggered
        mc_trigger = TriggeredText.objects.create(name="MC Advice", description="Desc",
                                                  message_kw="foo", message_fr="le foo", message_en="yo foo",
                                                  destination='CHW')
        mc_trigger.triggers.add(mc_type)

        # make sure our result is the same, that the new trigger doesn't go off
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(1, len(triggers))
        self.assertEquals(he_trigger.pk, triggers[0].pk)

        # add he to our mc trigger
        mc_trigger.triggers.add(he_type)

        # make sure we still only match the first trigger
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(1, len(triggers))
        self.assertEquals(he_trigger.pk, triggers[0].pk)

        # add mc to our report
        report.fields.create(type=mc_type)

        # make sure we only get one result back, but that it is the alert that 
        # matches more than one field
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(1, len(triggers))
        self.assertEquals(mc_trigger.pk, triggers[0].pk)

        # create a supervisor trigger that will match
        sup_trigger = TriggeredText.objects.create(name="SUP Advice", description="Desc",
                                                   message_kw="foo", message_fr="le foo", message_en="yo foo",
                                                   destination='SUP')
        sup_trigger.triggers.add(he_type)

        # make sure we get two matches then
        triggers = TriggeredText.get_triggers_for_report(report)
        self.assertEquals(2, len(triggers))
        self.assertEquals(mc_trigger.pk, triggers[0].pk)
        self.assertEquals(sup_trigger.pk, triggers[1].pk)

class TestTriggers (TestScript):
    apps = (App, ReporterApp)
    fixtures = ("fosa_location_types", "fosa_test_locations", "groups", "reporting", "test_triggers" )

    testTriggers = """
       1 > REG 4234567890123456 05094 en
       1 < Thank you for registering at Gashora
       2 > SUP 4234567890123451 05094 en
       2 < Thank you for registering at Gashora
       3 > SUP 4234567890123411 05096 fr
       3 < Nous vous remercions de vous etre enregistrer a la clinique Gashora Hospital
       1 > pre 123459 1965 he ma
       2 < 1: Alert to supervisor about ma-he
       3 < 1: Alert to district supervisor about he (fr)
       1 < Advice about ma.
       2 < 1: Pregnancy Report: Patient=123459, Location=Gashora, Date=1965, Hemorrhaging/Bleeding, Malaria
    """

class TestApp (TestScript):
    apps = (App, ReporterApp)

    fixtures = ("fosa_location_types", "fosa_test_locations", "groups", "reporting")

    testRegister = """
        2 > reg 1234567890123456 05
        2 < Iyi nimero y'ibitaro ntizwi: 05
        1 > reg asdf
        1 < The correct message format is: REG YOUR_ID CLINIC_ID LANG VILLAGE
        1 > reg 1234567890123456 01
        1 < Iyi nimero y'ibitaro ntizwi: 01
        1 > reg 1234567890123456 01001 en
        1 < Thank you for registering at Biryogo
        3 > REG 1234567890123456 01001 en
        3 < Thank you for registering at Biryogo

        # testing the default language
        30 > REG 1234567890123456 01001
        30 < Murakoze kwiyandikisha kuri iki kigo nderabuzima Biryogo
        30 > WHO
        30 < You are a CHW, located at Biryogo, you speak Kinyarwanda

        4 > WHO
        4 < Ntabwo dusobanukiwe, ntibyumvikana
        5 > REG 1234567890123458 01001 en
        5 < Thank you for registering at Biryogo
        5 > WHO
        5 < You are a CHW, located at Biryogo, you speak English
        5 > REG 1234567890123458 01001 EN
        5 < Thank you for registering at Biryogo
        5 > WHO
        5 < You are a CHW, located at Biryogo, you speak English

        # village names
        4 > REG 1234567890123459 01001 en foo
        4 < Thank you for registering at Biryogo
        4 > WHO
        4 < You are a CHW, located at Biryogo (foo), you speak English
        5 > REG 1234567890123459 01001 foo en
        5 < Thank you for registering at Biryogo
        5 > WHO
        5 < You are a CHW, located at Biryogo (foo), you speak English

    """
    
    testSupervisor = """
        1 > sup 1234567890123456 05094 en    
        1 < Thank you for registering at Gashora 
        4 > WHO
        4 < Ntabwo dusobanukiwe, ntibyumvikana
        1 > who   
        1 < You are a Supervisor, located at Gashora, you speak English

        2 > sup 1234567890123451 048547 fr
        2 < Iyi nimero y'ibitaro ntizwi: 048547
        3 > SUP 1234567890123452 048547 fr
        3 < Iyi nimero y'ibitaro ntizwi: 048547
    """
    
    testCC = """
        101 > reg 2234567890123456 05094 en
        101 < Thank you for registering at Gashora
        102 > sup 3234567890123456 05094 en
        102 < Thank you for registering at Gashora
        101 > bir 101 01 bo
        101 < Thank you! Birth report submitted successfully.
        102 < 101: Birth Report: Patient=101, Location=Gashora, Male, Child Number=1.00
        103 > sup 4234567890123456 05094 en 
        103 < Thank you for registering at Gashora
        101 > bir 101 01 bo
        101 < Thank you! Birth report submitted successfully.
        102 < 101: Birth Report: Patient=101, Location=Gashora, Male, Child Number=1.00
        103 < 101: Birth Report: Patient=101, Location=Gashora, Male, Child Number=1.00
    """
    
    testPregnancy = """
        1 > pre 4234567890123456 1982
        1 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        1 > REG 4234567890123456 01001 en
        1 < Thank you for registering at Biryogo
        1 > pre 10003 10.04.2009
        1 < Thank you! Pregnancy report submitted successfully.
        1 > LAST
        1 < Pregnancy Report: Patient=10003, Location=Biryogo, Date=10.04.2009
        1 > pre 10003 10.04.2009 68kpp
        1 < Thank you! Pregnancy report submitted successfully.
        1 > LAST
        1 < Pregnancy Report: Patient=10003, Location=Biryogo, Date=10.04.2009, Mother weight=68.00
        1 > pre 10003 1982 ho ma fe 
        1 < Thank you! Pregnancy report submitted successfully.
        1 > pre 10003 14.4.2010 ho ma fe 
        1 < Thank you! Pregnancy report submitted successfully.
        1 > pre 10003 14.14.2010 ho ma fe 
        1 < Invalid date format, must be in the form: DD.MM.YYYY
        1 > pre 10003 1982 HO MA fe 
        1 < Thank you! Pregnancy report submitted successfully.
        1 > pre 10003 1982 ho xx fe
        1 < Error.  Unknown action code: xx.
        1 > pre 10003 1982 ho cl fe 
        1 < Error.  You cannot give more than one location code
        1 > pre 10003 1982 ho fe cl 
        1 < Error.  You cannot give more than one location code
        1 > Pre 10003 1982 ho cl fE 
        1 < Error.  You cannot give more than one location code
        1 > pre 10003 1982 ho cl fe 21
        1 < Error.  Unknown action code: 21.  You cannot give more than one location code
        1 > pre 10003 1982 ma cl fe 21 
        1 < Error.  Unknown action code: 21.
        1 > pre
        1 < The correct format message is: PRE MOTHER_ID LAST_MENSES ACTION_CODE LOCATION_CODE MOTHER_WEIGHT
    """	
    
    testRisk = """
        1 > risk 10003 ho
        1 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        1 > pre 10003 1982
        1 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        1 > REG 4234567890123456 01001 en
        1 < Thank you for registering at Biryogo        
        1 > pre 10003 1982
        1 < Thank you! Pregnancy report submitted successfully.
        1 > last
        1 < Pregnancy Report: Patient=10003, Location=Biryogo, Date=1982
        1 > risk 10003 ho
        1 < Thank you! Risk report submitted successfully.
        1 > last
        1 < Risk Report: Patient=10003, Location=Biryogo, At home
        1 > risk 10003 ho 68k he
        1 < Thank you! Risk report submitted successfully.
        1 > LAST
        1 < Risk Report: Patient=10003, Location=Biryogo, At home, Mother weight=68.00, Hemorrhaging/Bleeding
        
        2 > risk 1000 ho fe ma
        2 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        2 > REG 4234567890123456 01001 en
        2 < Thank you for registering at Biryogo
        2 > risk 1000 ho fe ma
        2 < Thank you! Risk report submitted successfully.
        
        3 > risk 1000 ho fe ma
        3 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        3 > REG 4234567890123456 01001 en
        3 < Thank you for registering at Biryogo
        3 > risk
        3 < The correct format message is: RISK MOTHER_ID ACTION_CODE LOCATION_CODE MOTHER_WEIGHT

        4 > risk 10004 ho
        4 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
    """	
    
    testBirth = """

        1 > REG 4234567890123456 05094 en
        1 < Thank you for registering at Gashora
        1 > bir 1234568 01 ho
        1 < Thank you! Birth report submitted successfully.
        1 > pre 123459 1965 ho ma
        1 < Thank you! Pregnancy report submitted successfully.
        1 > bir 123459 01
        1 < Thank you! Birth report submitted successfully.
        1 > bir 123459 01 ho ma 5.43k 3.2cm
        1 < Thank you! Birth report submitted successfully.
        1 > bir 123459 02 ho ma 5.43cm 3.2kg
        1 < Thank you! Birth report submitted successfully.
        1 > last
        1 < Birth Report: Patient=123459, Location=Gashora, At home, Malaria, MUAC=5.43, Child weight=3.20, Child Number=2.00
        1 > bir 123459 03 ho ma 5.43cm 3.2kg 10.4.2010
        1 < Thank you! Birth report submitted successfully.
        1 > last
        1 < Birth Report: Patient=123459, Location=Gashora, Date=10.04.2010, At home, Malaria, MUAC=5.43, Child weight=3.20, Child Number=3.00
    """    
    
    testChildHealth = """

        1 > REG 4234567890123456 05094 en
        1 < Thank you for registering at Gashora
        1 > pre 123459 1965 ho ma
        1 < Thank you! Pregnancy report submitted successfully.
        1 > chi 1234568
        1 < The correct format message is: CHI MOTHER_ID CHILD_NUM CHILD_DOB MOVEMENT_CODE ACTION_CODE MUAC WEIGHT
        1 > chi 1234568 01 ho
        1 < Thank you! Child health report submitted successfully.
        1 > chi 123459 2 ho 
        1 < Thank you! Child health report submitted successfully.
        1 > chi 123459 3 ho ma 5.43k 3.2cm
        1 < Thank you! Child health report submitted successfully.
        1 > chi 123459 1 ho ma 5.43cm 3.2kg
        1 < Thank you! Child health report submitted successfully.
        1 > last
        1 < Child Health Report: Patient=123459, Location=Gashora, At home, Malaria, MUAC=5.43, Child weight=3.20, Child Number=1.00
        1 > chi 123459 1 ho ma 5.43cm 3.2kg 10.04.2010
        1 < Thank you! Child health report submitted successfully.
        1 > last
        1 < Child Health Report: Patient=123459, Location=Gashora, Date=10.04.2010, At home, Malaria, MUAC=5.43, Child weight=3.20, Child Number=1.00
        1 > chi 12345 4 ho 3.3k
        1 < Thank you! Child health report submitted successfully.
        1 > last
        1 < Child Health Report: Patient=12345, Location=Gashora, At home, Child weight=3.30, Child Number=4.00
    """    

    # define your test scripts here.
    # e.g.:
    #
    # testRegister = """
    #   8005551212 > register as someuser
    #   8005551212 < Registered new user 'someuser' for 8005551212!
    #   8005551212 > tell anotheruser what's up??
    #   8005550000 < someuser said "what's up??"
    # """
    #
    # You can also do normal unittest.TestCase methods:
    #
    # def testMyModel (self):
    #   self.assertEquals(...)
