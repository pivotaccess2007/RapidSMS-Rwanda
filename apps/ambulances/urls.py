#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import ambulances.views as views

urlpatterns = patterns('',
    url(r'^ambulances$', views.ambulances),
    url(r'^ambulances/alphabetically/(?P<letter>\w)$', views.ambulances_by_alphabet),
    url(r'^ambulances/location/(?P<loc>\d+)$', views.ambulances_by_location),
    url(r'^ambulances/driver/add$', views.ambulance_driver_add),
    url(r'^ambulances/driver/delete$', views.ambulance_driver_delete),
    url(r'^ambulances/add$', views.ambulance_add)
)
