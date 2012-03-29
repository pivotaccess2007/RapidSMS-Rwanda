#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import csv
from datetime import date, timedelta
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseRedirect,Http404
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.db import transaction, connection
from django.db.models import Q

from rapidsms.webui.utils import *
from django.contrib.auth.models import *
from django.shortcuts import render_to_response

@permission_required('web_test2.can_view')
def home(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('web_test2/index2.html',my_rc)
