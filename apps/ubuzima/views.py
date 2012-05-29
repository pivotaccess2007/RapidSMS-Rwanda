#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

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
from django.db.models import Count,Sum

from rapidsms.webui.utils import *
from reporters.models import *
from reporters.utils import *
from sys import getdefaultencoding
from ubuzima.models import *
from ubuzima.enum import *
from django.contrib.auth.models import *


@permission_required('ubuzima.can_view')
#@require_GET
@require_http_methods(["GET"])
def index(req,**flts):
    try:
        p = UserLocation.objects.get(user=req.user)
    except UserLocation.DoesNotExist,e:
        return render_to_response(req,"404.html",{'error':e})
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reports=matching_reports(req,filters)
    req.session['track']=[
       {'label':'Pregnancy',          'id':'allpreg',
       'number':len(reports.filter(type=ReportType.objects.get(name = 'Pregnancy')))},
       {'label':'Birth',            'id':'bir',
       'number':len(reports.filter(type=ReportType.objects.get(name = 'Birth')))},
        {'label':'ANC',            'id':'anc',
       'number':len(reports.filter(type=ReportType.objects.get(name = 'ANC')))},
       {'label':'Risk', 'id':'risk',
       'number':len(reports.filter(type=ReportType.objects.get(name = 'Risk')))},
       {'label':'Child Health',           'id':'chihe',
       'number':len(reports.filter(type=ReportType.objects.get(name = 'Child Health')))},]
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    if req.REQUEST.has_key('csv'):
        heads=['ReportID','Date','Location','Type','Reporter','Patient','Message']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        seq=[]
        for r in reports:
            try:
                seq.append([r.id, r.created,r.location,r.type,r.reporter.alias,r.patient.national_id, r.summary()])
            except Reporter.DoesNotExist:
                continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req,
            "ubuzima/index.html", {
            "reports": paginated(req, reports, prefix="rep"),'usrloc':UserLocation.objects.get(user=req.user),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
             'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]
        })

@permission_required('ubuzima.can_view')
@require_http_methods(["GET"])
def by_patient(req, pk):
    patient = get_object_or_404(Patient, pk=pk)
    reports = Report.objects.filter(patient=patient).order_by("-created")
    
    # look up any reminders sent to this patient
    reminders = []
    for report in reports:
        for reminder in report.reminders.all():
            reminders.append(reminder)

    return render_to_response(req,
                              "ubuzima/patient.html", { "patient":    patient,
                                                        "reports":    paginated(req, reports, prefix="rep"),
                                                        "reminders":  reminders })
    
@require_http_methods(["GET"])
def by_type(req, pk, **flts):
    report_type = get_object_or_404(ReportType, pk=pk)
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reports = matching_reports(req,filters).filter(type=report_type).order_by("-created")
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    return render_to_response(req,
                              "ubuzima/type.html", { "type":    report_type,
                                                     "reports":    paginated(req, reports, prefix="rep"),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1] })
    

@require_http_methods(["GET"])
def view_report(req, pk):
    report = get_object_or_404(Report, pk=pk)
    
    return render_to_response(req,
                              "ubuzima/report.html", { "report":    report })
    
    
@require_http_methods(["GET"])
def by_reporter(req, pk, **flts):
    reporter = Reporter.objects.get(pk=pk)
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reports = matching_reports(req,filters).filter(reporter=reporter).order_by("-created")
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    return render_to_response(req,
                              "ubuzima/reporter.html", { "reports":    paginated(req, reports, prefix="rep"),
                                                         "reporter":   reporter,'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1] })
@require_http_methods(["GET"])
def by_location(req, pk, **flts):
    location = get_object_or_404(Location, pk=pk)
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reports = matching_reports(req,filters).filter(location=location).order_by("-created")
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    
    return render_to_response(req,
                              "ubuzima/location.html", { "location":   location,
                                                         "reports":   paginated(req, reports, prefix="rep"),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1] })
@require_http_methods(["GET"])
def triggers(req):
    triggers = TriggeredText.objects.all()
    
    return render_to_response(req,
                              'ubuzima/triggers.html', { 'triggers': paginated(req, triggers, prefix='trg') } )
    
 
@require_http_methods(["GET"])
def trigger(req, pk):
    trigger = TriggeredText.objects.get(pk=pk)
    return render_to_response(req, 'ubuzima/trigger.html',
            { 'trigger': trigger })

def match_filters(req,diced,alllocs=False):
    rez = {}
    pst = None
    try:
        rez['date__gte'] = diced['period']['start']
        rez['date__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass
    try:
        if alllocs: raise KeyError
        loc = int(req.REQUEST['location'])
        rez['reporter__location__id'] = loc
    except KeyError:
        try:
            lox = LocationShorthand.objects.filter(district = int(req.REQUEST['district']))
            rez['reporter__location__in'] = [x.original for x in lox]
        except KeyError:
            try:
                lox = LocationShorthand.objects.filter(province = int(req.REQUEST['province']))
                rez['reporter__location__in'] = [x.original for x in lox]
            except KeyError:
                pass

    return rez

def match_filters_fresher(req):
    pst={}
    try:
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='Health Centre':
            loc=uloc.location.id
            pst['reporter__location__id'] = loc
        elif uloc and uloc.location.type.name=='District':   
            dst=uloc.location.id
            lox = LocationShorthand.objects.filter(district =dst )
            pst['reporter__location__in'] = [x.original for x in lox]
        elif uloc and uloc.location.type.name=='Province':
            prv=uloc.location.id  
            lox = LocationShorthand.objects.filter(province =prv )
            pst['reporter__location__in'] = [x.original for x in lox]

    except UserLocation.DoesNotExist:
        pass
    return pst

def matching_refusal(req,diced,alllocs=False):
    rez = {}
    pst={}
    try:
        rez['created__gte'] = diced['period']['start']
        rez['created__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass
    try:
        if alllocs: raise KeyError
        loc = int(req.REQUEST['location'])
        rez['reporter__location__id'] = loc
    except KeyError:
        try:
            lox = LocationShorthand.objects.filter(district = int(req.REQUEST['district']))
            rez['reporter__location__in'] = [x.original for x in lox]
        except KeyError:
            try:
                lox = LocationShorthand.objects.filter(province = int(req.REQUEST['province']))
                rez['reporter__location__in'] = [x.original for x in lox]
            except KeyError:
                pass
    try:
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='Health Centre':
            loc=uloc.location.id
            pst['reporter__location__id'] = loc
        elif uloc and uloc.location.type.name=='District':   
            dst=uloc.location.id
            lox = LocationShorthand.objects.filter(district =dst )
            pst['reporter__location__in'] = [x.original for x in lox]
        elif uloc and uloc.location.type.name=='Province':
            prv=uloc.location.id  
            lox = LocationShorthand.objects.filter(province =prv )
            pst['reporter__location__in'] = [x.original for x in lox]

    except UserLocation.DoesNotExist:
        pass

    if rez:
        ans = Refusal.objects.filter(**rez)
    else:
       ans = Refusal.objects.all()

    if pst:
        ans = ans.filter(**pst)
    
    return ans
    

def matching_reports(req, diced, alllocs = False):
    rez = {}
    pst = {}
    try:
        rez['created__gte'] = diced['period']['start']
        rez['created__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass

    try:
        if alllocs: raise KeyError
        loc = int(req.REQUEST['location'])
        rez['location__id'] = loc
    except KeyError:
        try:
            dst=int(req.REQUEST['district'])
            lox = LocationShorthand.objects.filter(district =dst )
            rez['location__in'] = [x.original for x in lox]
        except KeyError:
            try:
                prv=int(req.REQUEST['province'])
                lox = LocationShorthand.objects.filter(province =prv )
                rez['location__in'] = [x.original for x in lox]
            except KeyError:    pass
    try:
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='Health Centre':
            loc=uloc.location.id
            pst['location__id'] = loc
        elif uloc and uloc.location.type.name=='District':   
            dst=uloc.location.id
            lox = LocationShorthand.objects.filter(district =dst )
            pst['location__in'] = [x.original for x in lox]
        elif uloc and uloc.location.type.name=='Province':
            prv=uloc.location.id  
            lox = LocationShorthand.objects.filter(province =prv )
            pst['location__in'] = [x.original for x in lox]

    except UserLocation.DoesNotExist:
        pass
            
    if rez:
        ans = Report.objects.filter(**rez).order_by("-created")
    else:
       ans = Report.objects.all().order_by("-created")
	
    if pst:
        ans = ans.filter(**pst).order_by("-created")
    return ans

def get_stats_track(req, filters):
    track = {'births':'Birth', 'pregnancy':'Pregnancy','anc':'ANC',
            'childhealth':'Child Health', 'risks': 'Risk','matdeaths':'Maternal Death','chideaths':'Child Death','newbdeaths':'New Born Death'}
    reps=matching_reports(req, filters)
    for k in track.keys():
        dem = reps.filter(type__name =
                track[k]).select_related('patient')
        #if k == 'pregnancy' or k == 'births':
           # dem = set([x.patient.id for x in dem])
        track[k]  = len(dem)
    repgrp        = ReporterGroup.objects.filter(title = 'CHW')
    
    track['chws'] = len(reps.filter(reporter__groups__in = repgrp))
    track['matdeaths']=len(fetch_maternal_death(reps))
    track['chideaths']=len(fetch_child_death(reps))
    track['newbdeaths']=len(fetch_newborn_death(reps))
    return track

@permission_required('ubuzima.can_view')
def view_stats_csv(req, **flts):
    filters = {'period':default_period(req)}
    track = get_stats_track(req, filters)
    rsp   = HttpResponse()
    rsp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
    wrt = csv.writer(rsp, dialect = 'excel-tab')
    wrt.writerows([['Births', 'Pregnancy', 'ANC',
        'Child Health', 'Maternal Risks', 'Community Health Workers']] +
        [[track[x] for x in ['births', 'pregnancy','anc', 'childhealth',
            'risks', 'chws']]])
    return rsp

def cut_date(str):
    stt = [int(x) for x in str.split('.')]
    stt.reverse()
    return date(* stt)

def default_period(req):
    if req.REQUEST.has_key('start_date') and req.REQUEST.has_key('end_date'):
        return {'start':cut_date(req.REQUEST['start_date']),
                  'end':cut_date(req.REQUEST['end_date'])}
    return {'start':date.today()-timedelta(datetime.datetime.today().day), 'end':date.today()}#In production
    #return {'start':date.today() - timedelta(date.today().day), 'end':date.today()}#locally

def default_location(req):
    
    try:
        dst = int(req.REQUEST['district'])
        loc = int(req.REQUEST['location']) if req.REQUEST.has_key('location') else 1
        uloc=UserLocation.objects.get(user=req.user)
        #reps = matching_reports(req, {'period':default_period(req)}, True).select_related('location')
        if uloc and uloc.location.type.name=='Health Centre':    return Location.objects.filter(id=uloc.location.id).extra(select = {'selected':'id = %d' % (uloc.location.id,)}).order_by('name')
        elif uloc and not uloc.location.type.name=='Health Centre':   return Location.objects.filter(id__in = [x.original.id for x in \
                LocationShorthand.objects.filter(district__id=dst).exclude(original__type__name__in = ["Hospital"])],).extra(select = {'selected':'id = %d' % (loc,)}).order_by('name')
        
    except KeyError:
        return []

def default_district(req):
    try:
        par = int(req.REQUEST['province'])
        sel = int(req.REQUEST['district']) if req.REQUEST.has_key('district') else 1
        typ = LocationType.objects.filter(name = 'District')[0].id
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='District':    return Location.objects.filter(id=uloc.location.id).extra(select = {'selected':'id = %d' % (uloc.location.id,)}).order_by('name') 
        if uloc and uloc.location.type.name=='Health Centre':
            loc= LocationShorthand.objects.get(original__id=uloc.location.id) 
            return Location.objects.filter(id = loc.district.id).extra(select = {'selected':'id = %d' % (loc.district.id,)}).order_by('name')          
        else:   return Location.objects.filter(type = typ, parent__id = par).extra(
                select = {'selected':'id = %d' % (sel,)}).order_by('name')
    except KeyError, IndexError:
        return []

def default_province(req):
    
    try:
        sel = int(req.REQUEST['province']) if req.REQUEST.has_key('province') else 1
        loc = LocationType.objects.filter(name = 'Province')[0].id
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='Province':    return Location.objects.filter(id=uloc.location.id).extra(select = {'selected':'id = %d' % (uloc.location.id,)}).order_by('name')
        elif uloc and not uloc.location.type.name=='Province':  
            ans=[]
            for an in uloc.location.ancestors():    ans.append(an.id)
            for an in Location.objects.filter(parent=uloc.location):    ans.append(an.id)    
            return Location.objects.filter(id__in=ans,type = loc).extra(select =
        {'selected':'id = %d' % (sel,)}).order_by('name')
    except IndexError:
        return []
    

#Reminders Logs! Ceci interroger la base de donnees et presenter a la page nommee remlog.html, toutes les rappels envoyes par le systeme!
@permission_required('ubuzima.can_view')
def view_reminders(req, **flts):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    template_name="ubuzima/remlog.html"
    rez=match_filters(req,filters)
    pst=match_filters_fresher(req)
    remlogs=Reminder.objects.filter(**rez).order_by('-date')
    if req.REQUEST.has_key('csv'):
        seq=[]
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in remlogs.filter(**pst):
            try:
                seq.append([r.date, r.type,[r.report.patient if r.report else None],r.reporter.location,r.reporter.connection().identity,["Supervisors: %s,"%str(sup.connection().identity) for sup in r.reporter.reporter_sups()]])
            except Exception: continue
        wrt.writerows([['Date','Type','Patient','Location','Reporter','Supervisor']]+seq)            
        return htp
    else:
        return render_to_response(req, template_name, { "reminders": paginated(req, remlogs.filter(**pst)),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
             'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

def remlog_by_type(req,pk,**flts):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    template_name="ubuzima/remlog.html"
    rem_type=ReminderType.objects.get(pk=pk)
    rez=match_filters(req,filters)
    remlogs=Reminder.objects.filter(type=rem_type,**rez).order_by('-date')
    if req.REQUEST.has_key('csv'):
        seq=[]
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in remlogs:
            try:
                seq.append([r.date, r.type,[r.report.patient if r.report else None],r.reporter.location,r.reporter.connection().identity,["Supervisors: %s,"%str(sup.connection().identity) for sup in r.reporter.reporter_sups()]])
            except Exception: continue
        wrt.writerows([['Date','Type','Patient','Location','Reporter','Supervisor']]+seq)            
        return htp
    else:
        return render_to_response(req, template_name, { "reminders": paginated(req, remlogs),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]})
#End of Reminders Logs!

#Alerts Logs! Ceci interroger la base de donnees et presenter a la page nommee alertlog.html, toutes les rappels envoyes par le systeme!
@permission_required('ubuzima.can_view')
def view_alerts(req, **flts):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    template_name="ubuzima/alertlog.html"
    rez=match_filters(req,filters)
    pst=match_filters_fresher(req)
    alertlogs=TriggeredAlert.objects.filter(**rez).order_by('-date')
    if req.REQUEST.has_key('csv'):
        seq=[]
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in alertlogs.filter(**pst):
            try:
                seq.append([r.date, r.trigger,[r.report.patient if r.report else None],r.reporter.location,r.reporter.connection().identity,["Supervisors: %s,"%str(sup.connection().identity) for sup in r.reporter.reporter_sups()]])
            except Exception: continue
        
        wrt.writerows([['DATE','TRIGGER','PATIENT','LOCATION','REPORTER','SUPERVISOR']]+seq)                   
        return htp
    else:
        return render_to_response(req, template_name, { "alerts": paginated(req, alertlogs.filter(**pst)),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
             'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]})
#End of Alerts logs


@permission_required('ubuzima.can_view')
def health_indicators(req, flts):
    reports = matching_reports(req, flts)
    fields = Field.objects.filter( report__in = reports).exclude(type__key__in = ['child_weight', 'child_number', 'muac', 'child_length', 'mother_weight','np']).exclude(type__category__name__in = ['Movement','Metric'])
    return fields.values('type__id','type__description').annotate(tot=Count('id')).order_by('type__description')

def the_chosen(hsh):
    ans = {}
    try:
        ans['province'] = int(hsh['province'])
        ans['district'] = int(hsh['district'])
        ans['location'] = int(hsh['location'])
    except KeyError:
        pass
    return ans

def map_pointers(req, lox, flts):
    dem = []
    try:
        try:
            loc = int(req.REQUEST['location'])
            dem = [Location.objects.get(id = loc).parent]
        except KeyError:
            req.REQUEST['district']
            dem = [x for x in lox if x.longitude]
            if not dem:
                {}['']
    except KeyError:
        pass
    if not dem:
        llv = set([x.location.id for x in matching_reports(req, flts)])
        dem = Location.objects.exclude(longitude = None).filter(id__in = llv).order_by('?')
    return dem[0:10] if len(dem) > 20 else dem

def location_name(req):
    ans = []
    try:
        prv = Location.objects.get(id = int(req.REQUEST['province']))
        ans.append(prv.name + ' Province')
        dst = Location.objects.get(id = int(req.REQUEST['district']))
        ans.append(dst.name + ' District')
        loc = Location.objects.get(id = int(req.REQUEST['loc']))
        ans.append(dst.name)
    except KeyError, DoesNotExist:
        pass
    ans.reverse()
    return ', '.join(ans)

def nine_months_ago(months = 9, auj = date.today()):
    ann, moi = auj.year, auj.month - months
    if moi < 1:
        moi = 12 + moi
        ann = ann - 1
    try:
        return date(ann, moi, auj.day)
    except ValueError:
        return date(ann, moi, 28)

def fetch_standards_ancs(qryset):
    ans=[]
    for x in qryset:
        try:  
            if (x.created.date() - x.date) < datetime.timedelta(140):
                ans.append(x)
        except: continue
    return ans

def fetch_edd_info(qryset, start, end):
    edd_start,edd_end=Report.calculate_last_menses(start),Report.calculate_last_menses(end)
    dem  = Report.objects.filter(type = ReportType.objects.get(name = 'Pregnancy'), date__gte =
            edd_start, date__lte = edd_end,location__in=qryset.values('location')).select_related('patient')
    return dem
def fetch_edd(start, end):
    edd_start,edd_end=Report.calculate_last_menses(start),Report.calculate_last_menses(end)
    dem  = Report.objects.filter(type = ReportType.objects.get(name = 'Pregnancy'), date__gte =
            edd_start, date__lte = edd_end).select_related('patient')
    return dem

def fetch_underweight_kids(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'child_weight'), value__lt = str(2.5) )).distinct()
def fetch_boys_kids(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'bo') )).distinct()
def fetch_girls_kids(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'gi') )).distinct()
def fetch_home_deliveries(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'ho') )).distinct()

def fetch_hosp_deliveries(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type__in=FieldType.objects.filter(key__in = ['hp','cl']) )).distinct()

def fetch_en_route_deliveries(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'or') )).distinct()
def fetch_unknown_deliveries(qryset):
    return qryset.exclude(fields__in=Field.objects.filter(type__in=FieldType.objects.filter(key__in = ['hp','cl','ho','or']) )).distinct()

def fetch_anc2_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'anc2'))).distinct()

def fetch_anc3_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'anc3'))).distinct()

def fetch_anc4_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'anc4'))).distinct()

def fetch_ancdp_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'dp'))).distinct()

class Gatherer:
    them   = {}
    qryset = None

    def __init__(self, qs):
        self.qryset = qs
        self.pull_from_db()

    def pull_from_db(self):
        rpt = ReportType.objects.get(name = 'Birth')
        prg = ReportType.objects.get(name = 'Pregnancy')
        mas = [x.patient.id for x in self.qryset.filter(type = rpt)]
        for m in self.qryset.filter(type = prg, patient__id__in = mas):
            self.append(m.patient.id, m)
        return

    def append(self, x, y):
        if self.them.has_key(x):
            self.them[x].add(y)
        else:
            self.them[x] = set()
            return self.append(x, y)
        return self

    def distinguish(self):
        stds, nstd = [], []
        for x in self.them.keys():
            if len(self.them[x]) > 3:
                stds.append(self.them[x])
            else:
                nstd.append(self.them[x])
        return (stds, nstd)

def anc_info(qryset):
    return Gatherer(qryset).distinguish()

def fetch_standard_ancs(qryset):
    return Gatherer(qryset).distinguish()[0]

def fetch_nonstandard_ancs(qryset):
    return Gatherer(qryset).distinguish()[1]

def get_patients(qryset):
    pats=set()
    for rep in qryset:
        pats.add(rep.patient)
    return pats

def fetch_anc1_info(qryset):
    return qryset.filter(type=ReportType.objects.get(name = 'Pregnancy'))

def fetch_all4ancs_info(qryset,jour):
    rps=Report.objects.filter(patient__in=Patient.objects.filter(id__in=fetch_anc4_info(qryset).values_list('patient')),type__name__in\
                    =["Pregnancy","ANC"],date__gte=nine_months_ago(9, jour))
    return Patient.objects.filter(id__in=fetch_anc3_info(rps).values_list('patient'))&Patient.objects.filter(id__in=fetch_anc2_info(rps)\
                                            .values_list('patient'))&Patient.objects.filter(id__in=fetch_anc1_info(rps).values_list('patient'))

def fetch_maternal_death(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'md'))).distinct()

def fetch_child_death(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'cd'))).distinct()

def fetch_newborn_death(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'nd'))).distinct()

def fetch_vaccinated_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type__in = FieldType.objects.filter(category=FieldCategory.objects.get(name='Vaccination')))).distinct()

def fetch_vaccinated_stats(reps):
    track={}
    for r in FieldType.objects.filter(category=FieldCategory.objects.get(name='Vaccination')): track[r.key]=reps.filter(fields__in = Field.objects.filter(type=FieldType.objects.get(key=r.key))).distinct()
    return track

def fetch_high_risky_preg(qryset):    
    return qryset.filter(fields__in = Field.objects.filter(type__in = FieldType.objects.filter(key__in =['ps','ds','sl','ja','fp','un','sa','co','he','pa','ma','sc','la'])))

def fetch_without_toilet(qryset):
    return qryset.filter(fields__in = Field.objects.filter(type = FieldType.objects.get(key ='nt')))

def fetch_without_hw(qryset):
    return qryset.filter(fields__in = Field.objects.filter(type = FieldType.objects.get(key ='nh')))

def get_important_stats(req, flts):
    rpt    = ReportType.objects.get(name = 'Birth')
    regula = matching_reports(req, flts)
    qryset = regula.filter(type = rpt).select_related('patient')
    ans    = [
   {'label':'Expected deliveries ',          'id':'expected',
   'number':len(fetch_edd_info(regula, flts['period']['start'], flts['period']['end']))},
   {'label':'Underweight Births',           'id':'underweight',
   'number':len(fetch_underweight_kids(qryset))},
   {'label':'Delivered at Home',            'id':'home',
   'number':len(fetch_home_deliveries(qryset))},
   {'label':'Delivered at Health Facility', 'id':'facility',
   'number':len(fetch_hosp_deliveries(qryset))},
   {'label':'Delivered en route',           'id':'enroute',
	'number':len(fetch_en_route_deliveries(qryset))},
    {'label':'Delivered Unknown',           'id':'unknown',
   'number':len(fetch_unknown_deliveries(qryset))}
   ]
    return ans

#View Stats by reports and on Graph view

#Risks Stats
def risk_details(req,**flts):
    filters   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    details=[]
    tf={}
    ftr=FieldType.objects.filter(category=FieldCategory.objects.get(name='Risk'))
    reps=matching_reports(req, filters).filter(type=ReportType.objects.get(name = 'Risk'))
    lxn,crd = location_name(req), map_pointers(req,
            filters['location'], filters)
    for f in ftr:
        tf[f.key]={}
        ans=[]
        for r in reps:
            try:
                fs=r.fields.filter(type=f)
                if fs:  ans.append(r)
            except Field.DoesNotExist:  pass 
        tf[f.key]={'id':f.key,'label':f.description,'reports':ans}
        details.append(tf[f.key])
                             
            
    return render_to_response(req, 'ubuzima/risk.html',
           {'track':details, 'filters':filters,
         'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,'coords':crd,'stattitle':'Risk Statistics',
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

def risk_stats(req,format,dat):
    filters   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    rez=[]
    f=FieldType.objects.get(key=dat)
    reps=matching_reports(req, filters).filter(type=ReportType.objects.get(name = 'Risk'))
    lxn,crd = location_name(req), map_pointers(req,
            filters['location'], filters)
    for r in reps:
            try:
                fs=r.fields.filter(type=f)
                if fs:  rez.append(r)
            except Field.DoesNotExist:  pass 
        
    if format == 'csv':
        seq=[]
        heads=['ReportID','Reporter', 'Location', 'Patient','ReportDetails','ExpectedDueDate','Supervisors']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in rez:
            try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.summary(), r.reporter.reporter_sups()])
            except Exception: continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req, ('ubuzima/riskdetails.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,
           'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1],
   'stattitle': {f.key:f.description,
     }[dat]})    


#End of Risks Stats

#Pregnancy stats

@permission_required('ubuzima.can_view')
def view_pregnancy(req, **flts):
    filters   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
   
    pregs = matching_reports(req, filters).filter(type=ReportType.objects.get(name = 'Pregnancy'))
    
    lxn,crd = location_name(req), map_pointers(req,
            filters['location'], filters)
    ans    = [
   {'label':'Total Pregnancy Reports',          'id':'allpreg',
   'number':len(pregs)},
   {'label':'High Risk Pregnancies',            'id':'hrpreg',
   'number':len(fetch_high_risky_preg(pregs))},
   {'label':'Pregnant without Toilet', 'id':'notoi',
   'number':len(fetch_without_toilet(pregs))},
   {'label':'Pregnant without Hand Washing station',           'id':'nohw',
   'number':len(fetch_without_hw(pregs))},
    
   ]

    return render_to_response(req, 'ubuzima/pregnancy.html',
           {'track':ans, 'filters':filters,
         'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,'coords':crd,
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

@permission_required('ubuzima.can_view')
def pregnancy_stats(req, format, dat):
    flts   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}

    lxn = location_name(req)

    pregs = matching_reports(req, flts).filter(type=ReportType.objects.get(name = 'Pregnancy'))

    rez = []
    if dat=='allpreg':
        rez=pregs
    elif dat=='hrpreg':
        rez=fetch_high_risky_preg(pregs)
    elif dat=='notoi':
        rez=fetch_without_toilet(pregs)
    elif dat=='nohw':
        rez=fetch_without_hw(pregs)
    
    if format == 'csv':
        seq=[]
        heads=['ReportID','Reporter', 'Location', 'Patient','ReportDetails','ExpectedDueDate','Supervisors']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in rez:
            try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.summary(), r.show_edd(), r.reporter.reporter_sups()] )
            except Exception: continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req, ('ubuzima/pregnancydetails.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),'filters':flts,
           'locationname':lxn,
   'stattitle': {'allpreg':'All Pregnancies','hrpreg':'High Risk Pregnancies',
          'notoi':'Pregnant  without Toilet',
                 'nohw':'Pregnant without Hand Washing station',
     }[dat]})


#end of pregnancy stats



#DEATH stats

def view_death(req, **flts):
    filters   = {'period':default_period(req),
                 'location':default_location(req),
                 'province':default_province(req),
                 'district':default_district(req)}

    reps = matching_reports(req, filters)
    chi_deaths = fetch_child_death(reps)
    mo_deaths = fetch_maternal_death(reps)
    nb_deaths = fetch_newborn_death(reps)
    lxn,crd = location_name(req), map_pointers(req,filters['location'], filters)
    ans=[{'label':'Maternal Death',          'id':'matde',
       'number':len(mo_deaths)},
       {'label':'Child Death',           'id':'chide',
       'number':len(chi_deaths)},{'label':'New Born Death',           'id':'newb',
       'number':len(nb_deaths)}]  
    
    return render_to_response(req, 'ubuzima/death.html',
           {'track':ans,'stat':{'matde':len(mo_deaths),'chide':len(chi_deaths),'newb':len(nb_deaths)}, 'filters':filters,'usrloc':UserLocation.objects.get(user=req.user),
         'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,'coords':crd,
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]}) 


def death_stats(req, format, dat):
    flts   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    lxn = location_name(req)
    reps = matching_reports(req, flts)
    rez = []
    if dat=='matde':
        rez=fetch_maternal_death(reps)
    elif dat=='chide':
        rez=fetch_child_death(reps)
    elif dat=='newb':
        rez=fetch_newborn_death(reps)
    if format == 'csv':
        seq=[]
        heads=['ReportID','Reporter', 'Location', 'Patient','ReportDetails','Supervisors']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in rez:
            try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.summary(), r.reporter.reporter_sups()] )
            except Exception: continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req, ('ubuzima/deathdetails.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,
   'stattitle': {'matde':'Maternal Death','chide':'Child Death','newb':'New Born Death', }[dat]})

#end of DEATH stats

#CHILD HEALTH stats
@permission_required('ubuzima.can_view')
def view_chihe(req, **flts):
    filters   = {'period':default_period(req),
                 'location':default_location(req),
                 'province':default_province(req),
                 'district':default_district(req)}

    chihe_reps =matching_reports(req, filters).filter(type = ReportType.objects.get(name = 'Child Health')).select_related('fields')
    vac_chihe_reps=fetch_vaccinated_stats(fetch_vaccinated_info(chihe_reps))
    lxn,crd = location_name(req), map_pointers(req,filters['location'], filters)

    ans=[]
    for v in vac_chihe_reps.keys():
        ans.append({'label':"Children vaccinated with %s"%v,'id':'%s'%v,'number':len(vac_chihe_reps[v])})   
    ans.append({'label':"ALL Children vaccinated ",'id':'all','number':len(fetch_vaccinated_info(chihe_reps))})
    return render_to_response(req, 'ubuzima/chihe.html',
           {'track':ans, 'filters':filters,
         'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,'coords':crd,
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

def chihe_stats(req, format, dat):
    flts   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}

    chihe_reps =matching_reports(req, flts).filter(type = ReportType.objects.get(name = 'Child Health')).select_related('fields')
    vac_chihe_reps=fetch_vaccinated_stats(fetch_vaccinated_info(chihe_reps))    
    lxn = location_name(req)
    rez = []
    for v in vac_chihe_reps.keys():        
        if dat=='%s'%v:
            rez=vac_chihe_reps[v]
    if dat=='all':
        rez=fetch_vaccinated_info(chihe_reps)
    
    if format == 'csv':
        seq=[]
        heads=['ReportID','Reporter', 'Location', 'Patient','ReportDetails','Supervisors']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in rez:
            try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.summary(), r.reporter.reporter_sups()] )
            except Exception: continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req, ('ubuzima/chihedetails.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,
   'stattitle': {'%s'%dat:'Children Vaccinated with %s'%dat}[dat]})

#end of CHILD HEALTH

#ANC stats
@permission_required('ubuzima.can_view')
def view_anc(req, **flts):
    filters   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    anc = ReportType.objects.get(name = 'ANC')
    preg= ReportType.objects.get(name = 'Pregnancy')
    reps = matching_reports(req, filters)
    anc_reps =reps.filter(type = anc).select_related('fields')
    preg_reps=reps.filter(type = preg).select_related('fields')
    lxn,crd = location_name(req), map_pointers(req,
            filters['location'], filters)
    ans    = [
   {'label':'Total ANC Reports',          'id':'allanc',
   'number':len(anc_reps)},
   {'label':'Attended First ANC (Pregnancy Registrations)',           'id':'anc1',
   'number':len(preg_reps)}, 
    {'label':'Standard First ANC','id':'stdanc','number':len(fetch_standards_ancs(preg_reps))},
   {'label':'Attended Second ANC',            'id':'anc2',
   'number':len(fetch_anc2_info(anc_reps))},
   {'label':'Attended Third ANC', 'id':'anc3',
   'number':len(fetch_anc3_info(anc_reps))},
   {'label':'Attended Fourth ANC',           'id':'anc4',
   'number':len(fetch_anc4_info(anc_reps))},
    {'label':'Attended all 4 ANCs',           'id':'all4ancs',
       'number':len(fetch_all4ancs_info(anc_reps,filters['period']['end']))},
   {'label':'Departed Patients',          'id':'ancdp',
   'number':len(fetch_ancdp_info(anc_reps))},{'label':'Patients Refused',          'id':'ref',
   'number':len(matching_refusal(req,filters))},
   ]

    return render_to_response(req, 'ubuzima/anc.html',
           {'track':ans,'usrloc':UserLocation.objects.get(user=req.user),'stat':{'ancs':len(anc_reps),'anc1':len(preg_reps),'ref':len(matching_refusal(req,filters)),'stdanc':len(fetch_standards_ancs(preg_reps)),'anc2':len(fetch_anc2_info(anc_reps)),'anc3':len(fetch_anc3_info(anc_reps)),'anc4':len(fetch_anc4_info(anc_reps)),'ancdp':len(fetch_ancdp_info(anc_reps))}, 'filters':filters,
         'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'locationname':lxn,'coords':crd,
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})
 
@permission_required('ubuzima.can_view')
def anc_stats(req, format, dat):
    flts   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    lxn = location_name(req)
    anc = ReportType.objects.get(name = 'ANC')
    preg= ReportType.objects.get(name = 'Pregnancy')
    reps = matching_reports(req, flts)
    anc_reps =reps.filter(type = anc).select_related('fields')
    preg_reps=reps.filter(type = preg).select_related('fields')
    
    rez = []
    if dat=='anc1':#This is equivalent to Pregnancy reports we have collected within this period!
        rez=preg_reps
    elif dat=='stdanc':
        rez=fetch_standards_ancs(preg_reps)
    elif dat=='anc2':
        rez=fetch_anc2_info(anc_reps)
    elif dat=='anc3':
        rez=fetch_anc3_info(anc_reps)
    elif dat=='anc4':
        rez=fetch_anc4_info(anc_reps)
    elif dat=='ancdp':
        rez=fetch_ancdp_info(anc_reps)
    elif dat=='all4ancs':
        rez=fetch_all4ancs_info(anc_reps,flts['period']['end'])
    elif dat=='allanc':
        rez=anc_reps
    elif dat=='ref':
        return render_to_response(req,('ubuzima/refdetails.html'),{'reports':paginated(req, matching_refusal(req,flts), prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),'filters':flts,
           'locationname':lxn,
   'stattitle': {'ref':'All Patients Refused',}[dat]})
    if format == 'csv':
        seq=[]
        heads=['ReportID','Reporter', 'Location', 'Patient','IsRisky', 'ReportDetails','ExpectedDueDate','Supervisors']
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        for r in rez:
            try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.is_risky(),r.summary(), r.show_edd(), r.reporter.reporter_sups()] )
            except Exception: 
                try: seq.append([r.id, r.reporter.connection().identity, r.location,
            r.patient,r.is_risky(),r.summary(),None,r.reporter.reporter_sups()] )
                except Exception: continue
        wrt.writerows([heads]+seq)
        return htp
    else:
        return render_to_response(req, ('ubuzima/ancdetails.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),'filters':flts,
           'locationname':lxn,
   'stattitle': {'allanc':'All ANC Attendance','anc1':'Attended First ANC (Pregnancy Registrations)','stdanc':'Standard First ANC Visits',
          'anc2':'Attended Second ANC',
                 'anc3':'Attended Third ANC',
             'anc4':'Attended Fourth ANC',
              'ancdp':'Departed Patients','all4ancs':'Attended all 4 ANCs Visits'}[dat]})
    

#end Of ANC!


#End of stats/graph

@permission_required('ubuzima.can_view')
def important_data(req, format, dat):
    flts   = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    rpt    = ReportType.objects.get(name = 'Birth')
    regula = matching_reports(req, flts)
    qryset = regula.filter(type = rpt).select_related('fields')
    rez = []
    if dat == 'expected':
        rez = fetch_edd_info(regula, flts['period']['start'], flts['period']['end'])
    elif dat == 'underweight':
        rez = fetch_underweight_kids(qryset)
    elif dat == 'home':
        rez = fetch_home_deliveries(qryset)
    elif dat == 'facility':
        rez = fetch_hosp_deliveries(qryset)
    elif dat == 'enroute':
        rez = fetch_en_route_deliveries(qryset)
    elif dat=='unknown':
        rez = fetch_unknown_deliveries(qryset)
    elif dat == 'standardanc':
        rez = fetch_standard_ancs(regula)
    elif dat == 'nonstandardanc':
        rez = fetch_nonstandard_ancs(regula)
    if format == 'csv':
        htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        try: wrt.writerows([[r.id, r.reporter.connection().identity, r.location,
            r.patient, r.created] for r in rez])
        except Exception: wrt.writerows([[r.id, r.reporter, r.location,
            r.patient, r.created] for r in rez])
        return htp
    else:
        return render_to_response(req, ('ubuzima/important.html'),
    {'reports':paginated(req, rez, prefix = 'imp'),'start_date':date.strftime(flts['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(flts['period']['end'], '%d.%m.%Y'),
   'stattitle': {'expected':'Expected deliveries in the next 30 days',
          'underweight':'Underweight Births',
                 'home':'Delievered at Home',
             'facility':'Delivered at Health Facility',
              'enroute':'Delivered en route',
                'unknown':'Delivered Unknown',}[dat]})

@permission_required('ubuzima.can_view')
def view_stats(req, **flts):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    track   = get_stats_track(req, filters)
    stt = filters['period']['start']
    fin = filters['period']['end']
    lox, lxn, crd = 0, location_name(req), map_pointers(req,
            filters['location'], filters)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
    return render_to_response(req, 'ubuzima/stats.html',
           {'track':track, 'filters':filters,'usrloc':UserLocation.objects.get(user=req.user),
       'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'coords':crd, 'location': lox, 'locationname':lxn,
           'chosen':the_chosen(req.REQUEST),
        'important':get_important_stats(req, filters),
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

@permission_required('ubuzima.can_view')
def view_indicator(req, indic, format = 'html'):
    resp=pull_req_with_filters(req)
    filters = resp['filters']
    indicator = FieldType.objects.get(id = indic) 
    pts     = matching_reports(req, filters).filter(fields__in = Field.objects.filter( type = indicator))
    heads   = ['Reporter', 'Location', 'Patient', 'Type', 'Date']
    resp['headers'] = heads
    resp['reports'] = paginated(req, pts, prefix = 'ind')
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    annot = resp['annot_l']
    ans_l, ans_m = {},{}
    if format == 'csv':
        rsp = HttpResponse()
        rsp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(rsp, dialect = 'excel-tab')
        wrt.writerows([heads] +
        [[x.reporter.connection().identity, x.location, x.patient, x.type, x.created] for x in pts])
        return rsp
    if pts.exists(): 
        pts_l = pts.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'pts' : pts_l, 'tot':pts.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])}

        pts_m = pts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'pts' : pts_m, 'tot': pts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}

    resp['track'] = {'items_l':ans_l, 'items_m':ans_m, 'months' : months_between(start,end), 'indicator': indicator}
    return render_to_response(req, ('ubuzima/indicator.html'), resp)

@permission_required('ubuzima.can_view')
def view_stats_reports_csv(req):
    filters = {'period':default_period(req),
             'location':default_location(req)}
    reports = matching_reports(req, filters).order_by('-created')
    seq=[]
    rsp     = HttpResponse()
    rsp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
    wrt = csv.writer(rsp, dialect = 'excel-tab')
    for r in reports:
        try: seq.append([r.created, r.reporter.connection().identity, r.location.name, str(r)])
        except Exception: continue
    wrt.writerows(seq)
    return rsp

def has_location(d, loc):
    try:
        lox = Location.objects.filter(parent__parent__parent = d, type__id = 5)
        for l in lox:
            if l.id == loc.id: return d
            a2 = has_location(l, loc)
            if a2: return a2
    except Location.DoesNotExist:
        pass
    return None

def district_and_province(loc, prov):
    dsid = LocationType.objects.get(name = 'District')
    for p in prov:
        dist = Location.objects.filter(type = dsid, parent = p)
        for d in dist:
            l = has_location(d, loc)
            if l: return (p, d)
    return None

@permission_required('ubuzima.can_view')
def shorthand_locations(__req):
    already = LocationShorthand.objects.all()
    newlocs = Location.objects.exclude(id__in = [int(x.original.id) for x in already])
    prid = LocationType.objects.get(name = 'Province')
    prov = Location.objects.filter(type = prid)
    for loc in newlocs:
        got = district_and_province(loc, prov)
        if not got: continue
        prv, dst = got
        ls = LocationShorthand(original = loc, district = dst, province = prv)
        ls.save()
    return HttpResponseRedirect('/ubuzima/stats')

@permission_required('ubuzima.can_view')
def error_display(req):
    them = ErrorNote.objects.all().order_by('-created')
    return render_to_response(req, 'ubuzima/errors.html',
            {'errors':paginated(req, them, prefix = 'err')})
@permission_required('ubuzima.can_view')
def agstats(req, **flts):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reps=matching_reports(req,filters)#all reports filtered
    woas=reps.values_list('location', flat=True).distinct()#all working areas(hc)
    lshs=LocationShorthand.objects.filter(original__in=woas) #all working shorthands



    agsts={}
    outsts=[]
    for hc in lshs:
	            #agsts[prv.id][dst.id][hc.id]={}
	            #agsts[prv.id][dst.id][hc.id]=reps.filter(location=hc)
	            sts={'birth':len(reps.filter(location=hc.original,type__name='Birth')),'pregnancy':len(reps.filter(location=hc.original,type__name='Pregnancy')),'anc':len(reps.filter(location=hc.original,type__name='ANC')),'chihe':len(reps.filter(location=hc.original,type__name='Child Health')),'risk':len(reps.filter(location=hc.original,type__name='Risk')),'matdeaths':len(fetch_maternal_death(reps.filter(location=hc.original))),'chideaths':len(fetch_child_death(reps.filter(location=hc.original))),'newbdeaths':len(fetch_newborn_death(reps.filter(location=hc.original))),'tot':len(reps.filter(location=hc.original)),'prv':hc.province.name,'dst':hc.district.name,'hc':hc.original.name}
	            outsts.append(sts)
    #print outsts
    lxn= location_name(req)
    return render_to_response(req, 'ubuzima/aggstats.html',
               {'track':paginated(req, outsts, prefix = 'imp'), 'filters':filters,
             'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),'usrloc':UserLocation.objects.get(user=req.user),
             'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
               'locationname':lxn,
               'postqn':(req.get_full_path().split('?', 2) + [''])[1]})
@permission_required('ubuzima.can_view')
def agstats_csv(req):
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    reps=matching_reports(req,filters)#all reports filtered
    woas=reps.values_list('location', flat=True).distinct()#all working areas(hc)
    lshs=LocationShorthand.objects.filter(original__in=woas) #all working shorthands



    agsts={}
    outsts=[]
    for hc in lshs:
	            #agsts[prv.id][dst.id][hc.id]={}
	            #agsts[prv.id][dst.id][hc.id]=reps.filter(location=hc)
	            sts={'birth':len(reps.filter(location=hc.original,type__name='Birth')),'pregnancy':len(reps.filter(location=hc.original,type__name='Pregnancy')),'anc':len(reps.filter(location=hc.original,type__name='ANC')),'chihe':len(reps.filter(location=hc.original,type__name='Child Health')),'risk':len(reps.filter(location=hc.original,type__name='Risk')),'matdeaths':len(fetch_maternal_death(reps.filter(location=hc.original))),'chideaths':len(fetch_child_death(reps.filter(location=hc.original))),'newbdeaths':len(fetch_newborn_death(reps.filter(location=hc.original))),'tot':len(reps.filter(location=hc.original)),'prv':hc.province.name,'dst':hc.district.name,'hc':hc.original.name}
	            outsts.append(sts)
    heads   = ['Province', 'District', 'Health Centre', 'Birth', 'Pregnancy','ANC','Child Health', 'Risk', 'Maternal Death','Child Death','New Born Death','Total']
    rsp     = HttpResponse()
    rsp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
    wrt = csv.writer(rsp, dialect = 'excel-tab')
    wrt.writerows([heads]+[[r['prv'], r['dst'], r['hc'], r['birth'], r['pregnancy'], r['anc'], r['chihe'], r['risk'], r['matdeaths'], r['chideaths'], r['newbdeaths'], r['tot']] for r in outsts])
    return rsp


@permission_required('ubuzima.can_view')
def dash(req):
    resp=pull_req_with_filters(req)
    resp['reports'] = paginated(req, matching_reports(req,resp['filters']), prefix="rep")
    return render_to_response(req,
            "ubuzima/dash.html", resp)
    

def child_locs(loc,filters):
    if loc.type.name == "Nation": return Location.objects.filter(parent=loc)
    elif loc.type.name == "Province": return filters['district'] if filters['district'] else Location.objects.filter(id__in =\
                                            LocationShorthand.objects.filter(province=loc).values_list('original'), type__name='Health Centre').order_by('name')
    elif loc.type.name == "District": return filters['location'] if filters['location'] else Location.objects.filter(id__in = LocationShorthand.objects.filter\
                                                                             (district=loc).values_list('original'), type__name='Health Centre').order_by('name')
    elif loc.type.name == "Health Centre": return filters['location'] if filters['location'] else Location.objects.filter(id=loc.id).order_by('name')

def pull_req_with_filters(req):
    try:
        p = UserLocation.objects.get(user=req.user)
        sel,prv,dst,lxn=None,None,None,None
        filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req),}
        try:    sel,lxn=int(req.REQUEST['location']),LocationShorthand.objects.get(original=Location.objects.get(pk=int(req.REQUEST['location'])))
        except KeyError:
            try:    sel,dst=int(req.REQUEST['district']),Location.objects.get(pk=int(req.REQUEST['district']))
            except KeyError:
                try:    sel,prv=int(req.REQUEST['province']),Location.objects.get(pk=int(req.REQUEST['province']))
                except KeyError:    pass
        if sel: sel=Location.objects.get(pk=sel)
        if not sel: sel = p.location 
        locs=child_locs(sel,filters)
        
        return {'usrloc':UserLocation.objects.get(user=req.user),'locs':locs,'annot':annot_val(sel),'annot_l':annot_locs_val(sel),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
             'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'sel':sel,'prv':prv,'dst':dst,'lxn':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]}
    except UserLocation.DoesNotExist,e:
        return render_to_response(req,"404.html",{'error':e})

def annot_val(loc):
    if loc.type.name == "Nation": return "location__parent__parent__parent__parent__name,location__parent__parent__parent__parent__pk"
    elif loc.type.name == "Province": return "location__parent__parent__parent__name,location__parent__parent__parent__pk"
    elif loc.type.name == "District": return "location__parent__parent__name,location__parent__parent__pk"
    else: return "location__name,location__pk"

def annot_locs_val(loc):
    if loc.type.name == "Nation": return "location__parent__parent__parent__name,location__parent__parent__parent__pk"
    elif loc.type.name == "Province": return "location__parent__parent__name,location__parent__parent__pk"
    elif loc.type.name == "District": return "location__name,location__pk"
    else: return "location__name,location__pk"

@permission_required('ubuzima.can_view')
def charts(req):
    resp = pull_req_with_filters(req)
    qryset, sel = matching_reports(req,resp['filters']).filter(type__name='Birth'), resp['sel']
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    
    ans, ans_c = qryset.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), None
    
    if qryset.exists():
        boys,girls,unwe,home,fac,route,unk = fetch_boys_kids(qryset),fetch_girls_kids(qryset),fetch_underweight_kids(qryset),\
                            fetch_home_deliveries(qryset),fetch_hosp_deliveries(qryset),fetch_en_route_deliveries(qryset),fetch_unknown_deliveries(qryset)
        fac_c, route_c, home_c, unk_c = fac.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), route.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), home.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'),unk.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_c = {'fac' : fac_c, 'route' : route_c, 'home': home_c, 'unk': unk_c}

    resp['track'] = {'label':['Boys','Girls','Underweight Births','Delivered at Home','Delivered at Health Facility','Delivered en route','Delivered Unknown'],'items':ans, 'items_c':ans_c, 'months' : months_between(start,end), 'qryset': qryset}
    return render_to_response(req, 'ubuzima/charts.html',
           resp)   


def months_between(start,end):
    months = []
    cursor = start

    while cursor <= end:
        m="%d-%d"%(cursor.month,cursor.year)
        if m not in months:
            months.append(m)
        cursor += timedelta(weeks=1)
    
    return months 

def months_enum():
    months=Enum('Months',JAN = 1, FEB = 2, MAR = 3, APR = 4, MAY = 5, JUN = 6, JUL = 7, AUG = 8, SEP = 9, OCT = 10, NOV = 11, DEC = 12)
    return months


def cut_reps_within_months(reps,start,end):
    months_b = months_between(start,end)
    months_e = months_enum()
    ans = []
    i=0
    for m in months_b:
        i=i+1
        ans.append( { 'month' : "%d,"%i+months_e.getByValue(m[0]).name + "-%d" % m[1] , 'data' : reps.filter( date__month = m[0] , date__year = m[1]).count()}  )
    
    return ans

def cut_births_within_months(births,start,end):
    months_b = months_between(start,end)
    months_e = months_enum()
    ans = []
    i=0
    for m in months_b:
        i=i+1
        ans.append( {'home': births.filter(fields__in=Field.objects.filter(type__key='ho'), date__month = m[0] , date__year = m[1]).count(),'fac': births.filter(fields__in=Field.objects.filter(type__key__in=['hp','cl']), date__month = m[0] , date__year = m[1]).count(),'route': births.filter( fields__in=Field.objects.filter(type__key='or'), date__month = m[0] , date__year = m[1]).count(),'total':births.filter(date__month = m[0] , date__year = m[1]).count(),'month' : "%d,"%i+months_e.getByValue(m[0]).name + "-%d" % m[1]}  )
    
    return ans
###START DEATH TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def death_report(req):

    resp = pull_req_with_filters(req)
    reports = matching_reports(req,resp['filters'])
    qryset = reports.filter(fields__in = Field.objects.filter(type__key__in = ["md","cd","nd"]))
    births = reports.filter(type__name='Birth', date__gte = resp['filters']['period']['start'], date__lte = resp['filters']['period']['end'])
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    annot = resp['annot_l']
    locs = resp['locs']
    ans_l, ans_m = {},{}
    resp['reports'] = paginated(req, qryset, prefix="rep")
    if qryset.exists():

        matde, chide, nebde = fetch_maternal_death(qryset),fetch_child_death(qryset),fetch_newborn_death(qryset) 
 
        matde_l,chide_l,nebde_l = matde.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), chide.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), nebde.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'matde' : matde_l, 'chide' : chide_l, 'nebde': nebde_l, 'tot': qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]) }

        matde_m, chide_m, nebde_m = matde.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), chide.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), nebde.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'matde' : matde_m, 'chide' : chide_m, 'nebde': nebde_m, 'tot': qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}

    resp['track'] = {'items_l':ans_l, 'items_m':ans_m, 'months' : months_between(start,end), 'bir_l': births.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), 'bir_m': births.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}
    return render_to_response(req, 'ubuzima/death_report.html',
           resp) 

###END OF DEATH TABLES, CHARTS, MAP

###START RISK TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def risk_report(req):

    resp = pull_req_with_filters(req)
    reports = matching_reports(req,resp['filters'])
    resp['reports'] = reports
    qryset = reports.filter(fields__in = Field.objects.filter(type__in = Field.get_risk_fieldtypes()))
    allpatients = Patient.objects.filter( id__in = reports.values('patient')) 
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    annot = resp['annot_l']
    resp['reports'] = paginated(req, qryset, prefix="rep")
    ans_l, ans_m = {},{}
    if qryset.exists():
        
        patients = allpatients.filter( id__in = qryset.values('patient'))
        alerts = qryset.filter( id__in = TriggeredAlert.objects.filter( report__in = qryset).values('report'))
        red_patients = patients.filter( id__in = alerts.values('patient'))
        yes_alerts = qryset.filter( id__in = TriggeredAlert.objects.filter( report__in = qryset, trigger__destination = "AMB", response = 'YES').values('report'))
        po_alerts = qryset.filter( id__in = TriggeredAlert.objects.filter( report__in = qryset, trigger__destination__in = ["SUP","DIS"], response = 'PO').values('report'))

        patients_l, alerts_l, red_patients_l, yes_alerts_l, po_alerts_l = patients.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), alerts.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), red_patients.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), yes_alerts.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), po_alerts.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'pats' : patients_l, 'alts' : alerts_l, 'rpats': red_patients_l, 'yalts': yes_alerts_l, 'palts': po_alerts_l, 'tot': qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]) }

        patients_m, alerts_m, red_patients_m, yes_alerts_m, po_alerts_m = qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('patient',distinct = True)).order_by('year','month'), alerts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), alerts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('patient',distinct = True)).order_by('year','month'), yes_alerts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), po_alerts.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'pats' : patients_m, 'alts' : alerts_m, 'rpats': red_patients_m, 'yalts': yes_alerts_m, 'palts': po_alerts_m, 'tot': qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}

    resp['track'] = {'items_l':ans_l, 'items_m':ans_m, 'months' : months_between(start,end), 'pats_l': allpatients.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), 'pats_m': reports.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('patient',distinct = True)).order_by('year','month')}
    return render_to_response(req, 'ubuzima/risk_report.html',
           resp) 

###END OF RISK TABLES, CHARTS, MAP


##START OF BIRTH TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def birth_report(req):
    resp=pull_req_with_filters(req)
    resp['reports']=matching_reports(req,resp['filters'])
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    #qryset = resp['reports'].filter(type__name='Birth')
    qryset = resp['reports'].filter(type__name='Birth', date__gte = start, date__lte = end )
    #print qryset.count()
    annot=resp['annot_l']
    locs=resp['locs']
    #print qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
    ans_l, ans_m = {}, {}
    resp['reports'] = paginated(req, qryset, prefix="rep")
    if qryset.exists(): 
        home,fac,route,unk = fetch_home_deliveries(qryset),fetch_hosp_deliveries(qryset),fetch_en_route_deliveries(qryset),fetch_unknown_deliveries(qryset)
  
        home_l,fac_l,route_l,unk_l = home.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), fac.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), route.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), unk.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'fac' : fac_l, 'route' : route_l, 'home': home_l, 'unk': unk_l, 'tot':qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])}

        fac_m, route_m, home_m, unk_m = fac.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), route.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), home.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'),unk.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'fac' : fac_m, 'route' : route_m, 'home': home_m, 'unk': unk_m, 'tot': qryset.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}

    resp['track'] = {'items_l':ans_l, 'items_m':ans_m, 'months' : months_between(start,end)}
    return render_to_response(req, 'ubuzima/birth_report.html',
           resp)
##END OF BIRTH TABLES, CHARTS, MAP

##START OF PREGNANCY TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def preg_report(req):
    resp=pull_req_with_filters(req)
    resp['reports']=matching_reports(req,resp['filters'])
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    preg = resp['reports'].filter(type__name='Pregnancy', date__gte = start, date__lte = end )
    annot = resp['annot_l']
    locs = resp['locs']
    ans_l, ans_m, rez = {}, {}, {}
    rez['%s__in'%annot.split(',')[1]] = [l.pk for l in locs]
    edd = fetch_edd( start, end).filter(** rez)
    resp['reports'] = paginated(req, preg, prefix="rep")
    if preg.exists() or edd.exists(): 
        preg_l, preg_risk_l, edd_l, edd_risk_l = preg.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), fetch_high_risky_preg(preg).values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), edd.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), fetch_high_risky_preg(edd).values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]) 

        ans_l = {'pre' : preg_l, 'prehr' : preg_risk_l, 'edd': edd_l, 'eddhr': edd_risk_l}

        preg_m, preg_risk_m, edd_m, edd_risk_m = preg.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), fetch_high_risky_preg(preg).extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), edd.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'),fetch_high_risky_preg(edd).extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'pre' : preg_m, 'prehr' : preg_risk_m, 'edd': edd_m, 'eddhr': edd_risk_m}
        
    resp['track'] = {'items_l':ans_l, 'items_m':ans_m, 'months' : months_between(start,end), 'months_edd' : months_between(Report.calculate_last_menses(start),Report.calculate_last_menses(end))}
    return render_to_response(req, 'ubuzima/preg_report.html',
           resp)
##END OF PREGNANCY TABLES, CHARTS, MAP

##START OF ADMIN TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def admin_report(req):
    resp=pull_req_with_filters(req)
    annot = resp['annot_l']
    locs = resp['locs']
    ans_l, ans_m, rez = {}, {}, {}
    rez['%s__in'%annot.split(',')[1]] = [l.pk for l in locs]
    reporters = Reporter.objects.filter(groups__title = 'CHW', ** rez)
    active = reporters.filter(connections__in = PersistantConnection.objects.filter(last_seen__gte = datetime.datetime.today().date() - timedelta(30)))
    resp['reports'] = paginated(req, reporters, prefix="rep")
    if reporters.exists() or active.exists(): 
        reporters_l, active_l = reporters.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]), active.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'rep' : reporters_l, 'act' : active_l}
        
    resp['track'] = {'items_l':ans_l}
    return render_to_response(req, 'ubuzima/admin_report.html',
           resp)
##END OF ADMIN TABLES, CHARTS, MAP

##START OF CHILD TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def child_report(req):
    resp=pull_req_with_filters(req)
    resp['reports']=matching_reports(req,resp['filters'])
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    qryset = resp['reports'].filter(type__name='Birth', date__gte = start, date__lte = end )
    annot=resp['annot_l']
    locs=resp['locs']
    resp['reports'] = paginated(req, qryset, prefix="rep")
    return render_to_response(req, 'ubuzima/child_report.html',
           resp)
##END OF CHILD TABLES, CHARTS, MAP
##START OF CHILD DETAILS TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def child_details_report(req, pk):
    resp=pull_req_with_filters(req)
    birth = Report.objects.get(pk = pk)
    child = birth.get_child()
    resp['reports'] = paginated(req, child['log'], prefix="rep")    
    resp['track'] = child
    return render_to_response(req, 'ubuzima/child_details.html',
           resp)
##END OF CHILD DETAILS TABLES, CHARTS, MAP

###Function to test any template
@permission_required('ubuzima.can_view')
def tests(req,dat):
    resp=pull_req_with_filters(req)
    annot=resp['annot']
    locs=resp['locs']
    qryset,ans=None,[]
    if dat == 'bir': 
        qryset = matching_reports(req,resp['filters']).filter(type__name='Birth')
        if qryset:
            boys,girls,unwe,home,fac,route,unk = fetch_boys_kids(qryset),fetch_girls_kids(qryset),fetch_underweight_kids(qryset),\
                            fetch_home_deliveries(qryset),fetch_hosp_deliveries(qryset),fetch_en_route_deliveries(qryset),fetch_unknown_deliveries(qryset)
            ans = [ 
                    {   'label':['Boys','Girls','Underweight Births','Delivered at Home','Delivered at Health Facility','Delivered en route','Delivered Unknown'],
                        'number':[boys.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        girls.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        unwe.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        home.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        fac.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        route.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),
                        unk.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0]),		
                        ],
                        'totals':[boys.count(),girls.count(),unwe.count(),home.count(),fac.count(),route.count(),unk.count()],
                        'totalglobal':qryset.count()
                    }
                ]
        else: pass
    resp['track'] = ans
    resp['lev']=annot.split(',')[0]
    return render_to_response(req, 'ubuzima/test.html',
           resp)


##DASHBOARD 
@permission_required('ubuzima.can_view')
def dashboard(req):
    resp=pull_req_with_filters(req)
    hindics = health_indicators(req,resp['filters'])
    resp['hindics'] = paginated(req, hindics, prefix = 'hind')
    return render_to_response(req,
            "ubuzima/dashboard.html", resp)
##END OF DASHBOARD

def fetch_pnc1_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'pnc1'))).distinct()

def fetch_pnc2_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'pnc2'))).distinct()

def fetch_pnc3_info(qryset):
    return qryset.filter(fields__in=Field.objects.filter(type=FieldType.objects.get(key = 'pnc3'))).distinct()


def fetch_eddanc2_info(qryset, start, end):
    eddanc2_start,eddanc2_end=Report.calculate_last_menses(start+datetime.timedelta(days=Report.DAYS_ANC2)),Report.calculate_last_menses(end+datetime.timedelta(days=Report.DAYS_ANC2))
    demo  = Report.objects.filter(type = ReportType.objects.get(name = 'Pregnancy'), date__gte =
            eddanc2_start, date__lte = eddanc2_end,location__in=qryset.values('location')).select_related('patient')
    return demo

def fetch_eddanc3_info(qryset, start, end):
    eddanc3_start,eddanc3_end=Report.calculate_last_menses(start+datetime.timedelta(days=Report.DAYS_ANC3)),Report.calculate_last_menses(end+datetime.timedelta(days=Report.DAYS_ANC3))
    demo  = Report.objects.filter(type = ReportType.objects.get(name = 'Pregnancy'), date__gte =
            eddanc3_start, date__lte = eddanc3_end,location__in=qryset.values('location')).select_related('patient')
    return demo

def fetch_eddanc4_info(qryset, start, end):
    eddanc4_start,eddanc4_end=Report.calculate_last_menses(start+datetime.timedelta(days=Report.DAYS_ANC4)),Report.calculate_last_menses(end+datetime.timedelta(days=Report.DAYS_ANC4))
    demo  = Report.objects.filter(type = ReportType.objects.get(name = 'Pregnancy'), date__gte =
            eddanc4_start, date__lte = eddanc4_end,location__in=qryset.values('location')).select_related('patient')
    return demo




###START ANC TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def anc_report(req):
    resp=pull_req_with_filters(req)
    reports = matching_reports(req,resp['filters'])
    resp['reports']=reports
    ##qryset=resp['reports'].filter(type__name='ANC')
    qryset = resp['reports'].filter(fields__in = Field.objects.filter(type__key__in = ["anc2","anc3","anc4"]))
    preg_reps=resp['reports'].filter(type__name='Pregnancy',date__gte = resp['filters']['period']['start'], date__lte = resp['filters']['period']['end'])
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    annot=resp['annot_l']
    locs=resp['locs']
    ans_l, ans_m = {},{}
    ans_t = qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

    if qryset.exists():
        eddanc2,eddanc3,eddanc4= fetch_eddanc2_info(qryset,start,end),fetch_eddanc3_info(qryset,start,end),fetch_eddanc4_info(qryset,start,end)
        anc1,anc2,anc3,anc4 = preg_reps,fetch_anc2_info(qryset),fetch_anc3_info(qryset),fetch_anc4_info(qryset)

        anc1_c = anc1.extra(select={'year': 'EXTRACT(year FROM date)','month': 'EXTRACT(month FROM date)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        anc2_c = anc2.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')
        anc3_c = anc3.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')
        anc4_c = anc4.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')
        eddanc2_c = eddanc2.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')
        eddanc3_c = eddanc3.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')
        eddanc4_c = eddanc4.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')


        ans_m = {'anc1_m' : anc1_c, 'anc2_m' : anc2_c, 'anc3_m': anc3_c, 'anc4_m': anc4_c, 'eddanc2_m': eddanc2_c, 'eddanc3_m': eddanc3_c, 'eddanc4_m': eddanc4_c,'tot_m': qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}


        anc1_l=anc1.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        anc2_l=anc2.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        anc3_l=anc3.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        anc4_l=anc4.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        eddanc2_l=eddanc2.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        eddanc3_l=eddanc3.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        eddanc4_l = eddanc4.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'anc1' : anc1_l, 'anc2' : anc2_l, 'anc3': anc3_l, 'anc4': anc4_l, 'eddanc2': eddanc2_l, 'eddanc3': eddanc3_l, 'eddanc4': eddanc4_l, 'tot':qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])}

    resp['track'] = {'items':ans_l, 'items_m':ans_m,'items_t':ans_t, 'months' : months_between(start,end)}
    return render_to_response(req, 'ubuzima/anc_report.html',resp)  

###END OF ANC TABLES, CHARTS, MAP



###START PNC TABLES, CHARTS, MAP
@permission_required('ubuzima.can_view')
def pnc_report(req):
    resp=pull_req_with_filters(req)
    resp['reports']=matching_reports(req,resp['filters'])
    ##qryset=resp['reports'].filter(type__name='ANC')
    qryset = resp['reports'].filter(fields__in = Field.objects.filter(type__key__in = ["pnc1","pnc2","pnc3"]))
    end = resp['filters']['period']['end']
    start = resp['filters']['period']['start']
    annot=resp['annot_l']
    locs=resp['locs']
    ans_l, ans_m = {},{}

    if qryset.exists():
        pnc1_m,pnc2_m,pnc3_m = fetch_pnc1_info(qryset),fetch_pnc2_info(qryset),fetch_pnc3_info(qryset)

        pnc1_c, pnc2_c, pnc3_c = pnc1_m.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), pnc2_m.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month'), pnc3_m.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')

        ans_m = {'pnc1_m' : pnc1_c, 'pnc2_m' : pnc2_c, 'pnc3_m': pnc3_c ,'tot_m': qryset.extra(select={'year': 'EXTRACT(year FROM created)','month': 'EXTRACT(month FROM created)'}).values('year', 'month').annotate(number=Count('id')).order_by('year','month')}



        pnc1_l= fetch_pnc1_info(qryset).values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        pnc2_l= fetch_pnc2_info(qryset).values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])
        pnc3_l= fetch_pnc3_info(qryset).values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])

        ans_l = {'pnc1' : pnc1_l, 'pnc2' : pnc2_l, 'pnc3': pnc3_l, 'tot':qryset.values(annot.split(',')[0],annot.split(',')[1]).annotate(number=Count('id')).order_by(annot.split(',')[0])}


    resp['track'] = {'items':ans_l, 'items_m':ans_m, 'months' : months_between(start,end)}
    return render_to_response(req, 'ubuzima/pnc_report.html',resp)  

###END OF PNC TABLES, CHARTS, MAP


#   TODO: Error-prone list should be done in raw SQL. Later.
