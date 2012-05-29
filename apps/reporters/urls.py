#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
import reporters.views as views


urlpatterns = patterns('',
    url(r'^reporters$',             views.index),
    url(r'^reporters/inactive/csv$', views.view_inactive_reporters_csv),
    url(r'^reporters/reporter$',             views.find_reporter),
    url(r'^reporters/location/(?P<pk>\d+)$',             views.reporters_by_location),
    url(r'^reporters/inactive$',             views.view_inactive_reporters),
    url(r'^reporters/inactive/location/(?P<pk>\d+)$',             views.inactive_reporters_location),
    url(r'^reporters/inactive/sup/(?P<pk>\d+)$',             views.inactive_reporters_sup),
    url(r'^reporters/add$',         views.add_reporter,  name="add-reporter"),
    url(r'^reporters/(?P<pk>\d+)$', views.edit_reporter, name="view-reporter"),
    url(r'^reporters/errors$',      views.error_list),
    url(r'^reporters/errors/csv$',      views.error_list_csv),
    
    url(r'^groups/$',            views.index),
    url(r'^groups/add$',         views.add_group),
    url(r'^groups/(?P<pk>\d+)$', views.edit_group),
    url(r'^reporters/active$',             views.view_active_reporters),
    url(r'^reporters/active/csv$',             views.view_active_reporters_csv),
    url(r'^reporters/import$',             views.import_reporters_from_excell,name='import_start'),
)
