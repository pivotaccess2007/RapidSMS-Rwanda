#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import csv
from datetime import date, timedelta
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.db import transaction, connection
from django.db.models import Q

from rapidsms.webui.utils import *
from reporters.models import *
from reporters.utils import *
from sys import getdefaultencoding
from ubuzima.models import *
from ambulances.models import *

CAN_HAVE_AMBULANCE = ['District', 'Hospital', 'Health Centre']

def alphabets(current = None):
    locs = Location.objects.filter(type__in = LocationType.objects.filter(name__in = CAN_HAVE_AMBULANCE))
    ans = list(set([x.name[0].upper() for x in locs]))
    ans.sort()
    return ans

@permission_required('reports.can_view')
def ambulances_by_alphabet(req, letter):
    locations = Location.objects.filter(type__in = LocationType.objects.filter(name__in = CAN_HAVE_AMBULANCE), name__startswith = letter.upper()).order_by('name')
    return render_to_response(req, 'ambulances/ambulances.html',
            {'locations': locations, 'alphabets': alphabets(letter), 'letter':letter})

@permission_required('reports.can_view')
def ambulances(req):
    #   locations = Location.objects.all().order_by('name')
    return render_to_response(req, 'ambulances/ambulances.html',
            {'locations': [], 'alphabets': alphabets(), 'letter':None})

@permission_required('reports.can_view')
def ambulances_by_location(req, loc):
    location = Location.objects.get(id = int(loc))
    drivers  = AmbulanceDriver.objects.filter(location = location).order_by('name')
    return render_to_response(req, 'ambulances/ambulance_locations.html',
            {'location': location, 'drivers': drivers})

@permission_required('reports.can_view')
def ambulance_driver_add(req):
    loxn   = Location.objects.get(id = int(req.POST['vers']))
    driver = AmbulanceDriver(phonenumber = req.POST['nimero'], name = req.POST['nom'], identity = req.POST['natid'], location = loxn)
    driver.save()
    return HttpResponseRedirect('/ambulances/location/%d' % (loxn.id,))

@permission_required('reports.can_view')
def ambulance_driver_delete(req):
    driver = AmbulanceDriver.objects.get(id = int(req.POST['drv']))
    loxn   = Location.objects.get(id = int(req.POST['vers']))
    driver.delete()
    return HttpResponseRedirect('/ambulances/location/%d' % (loxn.id,))

@permission_required('reports.can_view')
def ambulance_add(req):
    loxn      = Location.objects.get(id = int(req.POST['vers']))
    ambulance = Ambulance(plates = req.POST['nimero'], station = loxn)
    ambulance.save()
    return HttpResponseRedirect('/ambulances/location/%d' % (loxn.id,))
