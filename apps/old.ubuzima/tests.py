from rapidsms.tests.scripted import TestScript
from app import App
from apps.reporters.app import App as ReporterApp

class TestApp (TestScript):
    apps = (App, ReporterApp)

    fixtures = ("fosa_location_types", "fosa_test_locations", "groups", "reporting" )

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
        102 < 101: bir 101 01 bo
        103 > sup 4234567890123456 05094 en 
        103 < Thank you for registering at Gashora
        101 > bir 101 01 bo
        101 < Thank you! Birth report submitted successfully.
        102 < 101: bir 101 01 bo
        103 < 101: bir 101 01 bo
    """
    
    testPregnancy = """
        1 > pre 4234567890123456 1982
        1 < Ugomba kubanza kwiyandikisha, koresha ijambo REG
        1 > REG 4234567890123456 01001 en
        1 < Thank you for registering at Biryogo
        1 > pre 10003 10.04.2009
        1 < Thank you! Pregnancy report submitted successfully.
        1 > LAST
        1 < type: Pregnancy patient: 10003 Date: 10.04.2009 fields:
        1 > pre 10003 10.04.2009 68kpp
        1 < Thank you! Pregnancy report submitted successfully.
        1 > LAST
        1 < type: Pregnancy patient: 10003 Date: 10.04.2009 fields: mother_weight=68.00
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
        1 < type: Pregnancy patient: 10003 Date: 1982 fields: 
        1 > risk 10003 ho
        1 < Thank you! Risk report submitted successfully.
        1 > last
        1 < type: Risk patient: 10003 fields: ho
        1 > risk 10003 ho 68k he
        1 < Thank you! Risk report submitted successfully.
        1 > LAST
        1 < type: Risk patient: 10003 fields: he, ho, mother_weight=68.00
        
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
        1 < type: Birth patient: 123459 fields: ma, ho, child_weight=3.20, muac=5.43, child_number=2.00
        1 > bir 123459 03 ho ma 5.43cm 3.2kg 10.4.2010
        1 < Thank you! Birth report submitted successfully.
        1 > last
        1 < type: Birth patient: 123459 Date: 10.04.2010 fields: ma, ho, child_weight=3.20, muac=5.43, child_number=3.00
       
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
        1 < type: Child Health patient: 123459 fields: ma, ho, child_weight=3.20, muac=5.43, child_number=1.00
        1 > chi 123459 01 ho ma 5.43cm 3.2kg 10.4.2010
        1 < Thank you! Child health report submitted successfully.
        1 > last
        1 < type: Child Health patient: 123459 Date: 10.04.2010 fields: ma, ho, child_weight=3.20, muac=5.43, child_number=1.00
        1 > chi 12345 4 ho 3.3k
        1 < Thank you! Child health report submitted successfully.
        1 > last
        1 < type: Child Health patient: 12345 fields: ho, child_weight=3.30, child_number=4.00
       
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
