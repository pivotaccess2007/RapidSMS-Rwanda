#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response
from django.views.decorators.cache import cache_page
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.decorators import login_required

from rapidsms.webui import settings
from ubuzima.views import *
from locations.models import Location, LocationType

def check_availability(req):
    return HttpResponse("OK")

def dashboard(req):
    
    return render_to_response(req, "dashboard.html")

def login(req, template_name="webapp/login.html"):
    '''Login to rapidsms'''
    # this view, and the one below, is overridden because 
    # we need to set the base template to use somewhere  
    # somewhere that the login page can access it.
    req.base_template = settings.BASE_TEMPLATE 
    #area={}
    #locs=Report.objects.values_list('location', flat=True).distinct()
    #req.session['locs']=locs
    #req.session['dst']=[ dst for dst in Location.objects.filter(id__in=LocationShorthand.objects.filter(original__in=locs).values_list('district', flat=True).distinct())]
    #req.session['prv']=[ prov for prov in Location.objects.filter(id__in=LocationShorthand.objects.filter(original__in=locs).values_list('province', flat=True).distinct())]
    
    #req.session['important']=get_important_stats(req, filters)
    
    return django_login(req, **{"template_name" : template_name})

def logout(req, template_name="webapp/loggedout.html"):
    '''Logout of rapidsms'''
    req.base_template = settings.BASE_TEMPLATE 
    return django_logout(req, **{"template_name" : template_name})

def working_area(req):
    area={}
    locs=Report.objects.values_list('location', flat=True).distinct()
    return render_to_response(req, "layout.html",{'locs':locs, 'z':"ZIGAMA"})

def matching_report(req, diced, alllocs = False):
    rez = {}
    pst = {}
    try:
        rez['created__gte'] = diced['period']['start']
        rez['created__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass
    return rez

