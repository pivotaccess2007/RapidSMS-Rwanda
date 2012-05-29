#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, csv, decimal
from django.core.management.base import NoArgsCommand
from locations.models import * #we are importing model classes from locations app
from ubuzima.models import *
from django.core import management


IMPORT_DIR = os.path.abspath("apps/ubuzima/import")

#the indexes in fosa_table.csv
PROVINCE_NAME = 5 
PROVINCE_CODE = 4
NAME = 2
CODE = 0
TYPE = 3
LONGITUDE = 11
LATITUDE = 10
PARENT = 17

# indexes in fosa_villages.csv
VILLAGE_NAME = 1
VILLAGE_CODE =  0
VILLAGE_DISTRICT_CODE = 6
VILLAGE_SECTOR_CODE = 7

#indexes for District.csv
DISTRICT_NAME = 2
DISTRICT_CODE = 1
DISTRICT_PROVINCE_CODE =  3

#indexes for Sector.csv
SECTOR_CODE = 1
SECTOR_NAME = 2
SECTOR_DISTRICT_CODE = 5

class Command(NoArgsCommand):
    
    
    def _csv(self, filename):
        """Returns a CSV reader for _filename_
           relative to the sources directory."""
        path = os.path.join(IMPORT_DIR, filename)
        return csv.reader(open(path, "rU"))
    
    
    def _hospital_name(self, original):
        return original.capitalize()
    
    
    def _loc_type (self, name):
        return LocationType.objects.get(name__iexact=name)
    
    
    def __init__(self):
        self.provinces = {}
        self.districts = {}
        self.sectors = {}
        self.hospitals = {}
        self.healthcentres = {}
    
    def handle_noargs(self, **options):
        #delete all locations before insertion, 
        #we might change this during production
        Location.objects.all().delete()
        
        #load location_types fixture
        management.call_command('loaddata', 'fosa_location_types.json')
        
        # init our reporter groups
        management.call_command('loaddata', 'groups.json')
        
        # init our reporting objects
        management.call_command('loaddata', 'reporting.json')
        
        rows = list(self._csv("fosa_table.csv"))

        rows = rows[1:]
        for row in rows:
            # ensure that the province exists
            province, p_created = \
                self._loc_type("province").locations.get_or_create(
                    name=row[PROVINCE_NAME].capitalize(),
                    code="0" + row[PROVINCE_CODE])

            if p_created:
                print ". Created Province: %s" % (province)
                self.provinces[province.code] = province


        district_rows = list(self._csv("District.csv"))
        district_rows = district_rows[1:]
        for row in district_rows:
            # ensure that the district exists, and is
            # linked to the province named on this row
            district, d_created = \
                    self._loc_type("district").locations.get_or_create(
                        parent = self.provinces[row[DISTRICT_PROVINCE_CODE]],
                        #parent = province,
                        name=row[DISTRICT_NAME].capitalize(),
                        code=row[DISTRICT_CODE]
                        )
            
            if d_created:
                    print ". Created District: %s" % (district)
                    self.districts[district.code] = district


        sector_rows = list(self._csv("Sector.csv"))

        sector_rows = sector_rows[1:] 
        for row in sector_rows:  
            # making sure the sector exist linked to the district
            sector, s_created = \
                    self._loc_type("sector").locations.get_or_create(
                    parent = self.districts[row[SECTOR_DISTRICT_CODE]],
                    #parent = district,
                    name=row[SECTOR_NAME].capitalize(),
                    code=row[SECTOR_CODE]
                    )
            if s_created:
                    print ". Created Sector: %s (%s)" % (sector, sector.code)
                    self.sectors[sector.code] = sector
                
        
        # second iteration: create all of the hospitals. we must do
        # this before the health centres, since many health centres
        # link (by name) to the hospitals before they are listed
        for row in rows:
            if row[TYPE] == "HD" or row[TYPE] == "HM":
                try:
                    # wooo geo co-ords!
                    lat = decimal.Decimal(row[LATITUDE])
                    lon = decimal.Decimal(row[LONGITUDE])
                
                # django doesn't accept invalid decimals, so
                # leave both fields null if they can't be cast
                except decimal.InvalidOperation:
                    lat = lon = None
                print "Adding Hopital: %s %s" % (row[NAME], row[CODE])
                hospital, created = \
                    self._loc_type("hospital").locations.get_or_create(
                        #parent=self.sectors[row[SECTOR_CODE]],
                        parent = sector,
                        name=self._hospital_name(row[NAME]),
                        code=fosa_to_code(row[CODE]),
                        latitude=lat,
                        longitude=lon
                        )

                if created:
                    print ". Created Hospital: %s" %\
                        (hospital)
                    self.hospitals[hospital.name] = hospital


        # third iteration: create all of the remaining health
        # centres, and link them back to the hospitals. this is
        # very similar to above, and should probably be refactored
        for row in rows:
            if row[TYPE] == "CS":

                # some locations are missing their
                # government FOSA CODE. this just
                # won't do, so skip it
                if not row[CODE]:
                    print "! Health Centre missing FOSA code: %s" % (row[NAME])
                    continue


                try:
                    # wooo geo co-ords!
                    lat = decimal.Decimal(row[LATITUDE])
                    lon = decimal.Decimal(row[LONGITUDE])
                
                # django doesn't accept invalid decimals, so
                # leave both fields null if they can't be cast
                except decimal.InvalidOperation:
                    lat = lon = None


                # resolve the hospital name into an object.
                # if the parent was invalid, skip this location
                try:
                    parent = self.hospitals[self._hospital_name(row[PARENT])]

                except KeyError:
                    print "! Unable to find parent hospital for HC: %s" % row[CODE]
                    continue

                healthcentre, created = \
                    self._loc_type("health centre").locations.get_or_create(
                        parent=parent,
                        name=row[NAME],
                        code=fosa_to_code(row[CODE]),
                        latitude=lat,
                        longitude=lon)

                if created:
                    print ". Created Health Centre: %s" %\
                        (healthcentre)
                        
            
                
        village_rows = list(self._csv("fosa_villages.csv"))
        
        
        village_rows = village_rows[1:]
        for row in village_rows:
            sectorCode = "0" + row[VILLAGE_SECTOR_CODE]
            if sectorCode in self.sectors:
                parent = self.sectors[sectorCode]
            else:
                print "Unable to find parent for village: %s (sector: %s)" % (row[VILLAGE_CODE], sectorCode)
                continue
            
            village, v_created= \
            self._loc_type("village").locations.get_or_create(
                parent=parent,
                name=row[VILLAGE_NAME].capitalize(),
                code=row[VILLAGE_CODE]
            )
            
            if v_created:
                print ". Created Village: %s" %  (village)
                
                
