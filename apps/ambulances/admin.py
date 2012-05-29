#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from ambulances.models import *


admin.site.register(AmbulanceDriver)
admin.site.register(Ambulance)
