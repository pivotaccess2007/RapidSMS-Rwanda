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

from rapidsms.webui.utils import *
from reporters.models import *
from reporters.utils import *
from sys import getdefaultencoding
from ubuzima.models import *
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
    for k in track.keys():
        dem = matching_reports(req, filters).filter(type__name =
                track[k]).select_related('patient')
        #if k == 'pregnancy' or k == 'births':
           # dem = set([x.patient.id for x in dem])
        track[k]  = len(dem)
    repgrp        = ReporterGroup.objects.filter(title = 'CHW')
    reps          = matching_reports(req, filters).filter(reporter__groups__in = repgrp)
    track['chws'] = len(reps)
    track['matdeaths']=len(fetch_maternal_death(matching_reports(req, filters)))
    track['chideaths']=len(fetch_child_death(matching_reports(req, filters)))
    track['newbdeaths']=len(fetch_newborn_death(matching_reports(req, filters)))
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
    return {'start':date.today() - timedelta(7), 'end':date.today()}#In production
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
    ans    = []
    return ans      #   For now.    TODO.
    fields = FieldType.objects.filter(has_value = False).select_related('fields')[0:1]
    for fld in fields:
        tot = 0
        for rep in matching_reports(req, flts)[0:2]:
            if not fld in [x.type for x in rep.fields.all()[0:2]]:
                continue
            tot += 1
        ans.append({'id':fld.id,
            'proper_name':fld.description,
            'instances_count':tot})
    return ans

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
        if x.date and (x.created.date() - x.date) < datetime.timedelta(140):
            ans.append(x)
    return ans

def fetch_edd_info(qryset, jour):
    #we dont have to pass this query set beacause a pregnancy report may be given any time!
    locs=set()
    for x in qryset:
        if x.location in locs: continue
        locs.add(x.location)
    preg = ReportType.objects.get(name = 'Pregnancy')
    dem  = Report.objects.filter(type = preg, date__gte =
            nine_months_ago(9, jour), location__in=locs).select_related('patient')
    seen = set()
    ans  = []
    for x in dem:
        if x.patient.id in seen:
            continue
        if x.show_edd() >= jour and x.show_edd()< (jour + datetime.timedelta(30)): ans.append(x)
        seen.add(x.patient.id)
    return ans

def fetch_underweight_kids(qryset):
    ftp = FieldType.objects.get(key = 'child_weight')
    ans = []
    for x in qryset:
        dem = x.fields.all()
        for y in dem:
            if y.type == ftp and float(y.value) < 2.5:
                ans.append(x)
    return ans

def fetch_home_deliveries(qryset):
    ans = []
    for x in qryset:
        if x.is_home():
            ans.append(x)
    return ans

def fetch_hosp_deliveries(qryset):
    ans  = []
    for x in qryset:
        if x.is_hosp():
            ans.append(x)
    return ans

def fetch_en_route_deliveries(qryset):
    ans = []
    for x in qryset:
        if x.is_route():
            ans.append(x)
    return ans
def fetch_unknown_deliveries(qryset):
    ans = []
    for x in qryset:
        if x.is_home() or x.is_route() or x.is_hosp():
            pass
        else:
            ans.append(x)
    return ans

def fetch_anc2_info(qryset):
    ftp = FieldType.objects.get(key = 'anc2')
    ans = []
    for x in qryset:
        if ftp in [y.type for y in x.fields.all()]:
            ans.append(x)
    return ans

def fetch_anc3_info(qryset):
    ftp = FieldType.objects.get(key = 'anc3')
    ans = []
    for x in qryset:
        if ftp in [y.type for y in x.fields.all()]:
            ans.append(x)
    return ans

def fetch_anc4_info(qryset):
    ftp = FieldType.objects.get(key = 'anc4')
    ans = []
    for x in qryset:
        if ftp in [y.type for y in x.fields.all()]:
            ans.append(x)
    return ans

def fetch_ancdp_info(qryset):
    ftp = FieldType.objects.get(key = 'dp')
    ans = []
    for x in qryset:
        if ftp in [y.type for y in x.fields.all()]:
            ans.append(x)
    return ans

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

def fetch_all4ancs_info(qryset,jour):
    reps=Report.objects.filter(type__in=ReportType.objects.filter(name__in=['Pregnancy','ANC']),date__gte = nine_months_ago(9, jour))
    ans  = []
    anc4=fetch_anc4_info(qryset)
    patientCounts = {}
    patientList=set()
    for rep in reps:
        patientList.add(rep.patient)
        patientCounts[rep.patient]={'count':0,'dates':set()}
    
    for x in reps:
        if x.patient in patientList:
            patientCounts[x.patient]['count']=patientCounts[x.patient]['count']+1
            patientCounts[x.patient]['dates'].add(x.date)
        if patientCounts[x.patient]['count'] >= 4 and x in anc4 and len(patientCounts[x.patient]['dates']) >= 4: ans.append(x)
    return ans

def fetch_maternal_death(qryset):
    deaths=[]
    for x in qryset:
        if x.is_maternal_death():
            deaths.append(x)
    return deaths

def fetch_child_death(qryset):
    deaths=[]
    for x in qryset:
        if x.is_child_death():
            deaths.append(x)
    return deaths

def fetch_newborn_death(qryset):
    deaths=[]
    for x in qryset:
        if x.is_newborn_death():
            deaths.append(x)
    return deaths

def fetch_vaccinated_info(qryset):
    vacs=[]
    for x in qryset:
        if x.was_vaccinated():
            vacs.append(x)
    return vacs

def fetch_vaccinated_stats(reps):
    track={}
    for vac in FieldType.objects.filter(category=FieldCategory.objects.get(name='Vaccination')).order_by('pk'):
        ans=[]
        for rep in reps:
            if rep.was_vaccinated_with(vac):
                ans.append(rep)
        track[vac]=ans
    return track

def fetch_high_risky_preg(qryset):
    ans=[]
    preg=qryset.filter(type=ReportType.objects.get(name='Pregnancy'))
    for x in preg:
        if x.is_high_risky_preg(): ans.append(x)
    return ans

def fetch_without_toilet(qryset):
    ans=[]
    preg=qryset.filter(type=ReportType.objects.get(name='Pregnancy'))
    for x in preg:
        if x.has_no_toilet(): ans.append(x)
    return ans

def fetch_without_hw(qryset):
    ans=[]
    preg=qryset.filter(type=ReportType.objects.get(name='Pregnancy'))
    for x in preg:
        if x.has_no_hw(): ans.append(x)
    return ans

def get_important_stats(req, flts):
    rpt    = ReportType.objects.get(name = 'Birth')
    regula = matching_reports(req, flts)
    qryset = regula.filter(type = rpt).select_related('patient')
    stds, nstd = Gatherer(regula).distinguish()
    ans    = [
   {'label':'Expected deliveries in the next 30 days',          'id':'expected',
   'number':len(fetch_edd_info(regula, flts['period']['end']))},
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
        rez = fetch_edd_info(regula, flts['period']['end'])
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
    hindics = health_indicators(req, filters)
    stt = filters['period']['start']
    fin = filters['period']['end']
    lox, lxn, crd = 0, location_name(req), map_pointers(req,
            filters['location'], filters)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
    return render_to_response(req, 'ubuzima/stats.html',
           {'track':track, 'filters':filters,'usrloc':UserLocation.objects.get(user=req.user),
          'hindics':paginated(req, hindics, prefix = 'hind'),
       'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
         'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),
           'coords':crd, 'location': lox, 'locationname':lxn,
           'chosen':the_chosen(req.REQUEST),
        'important':get_important_stats(req, filters),
          'targets':HealthTarget.objects.all(),
           'postqn':(req.get_full_path().split('?', 2) + [''])[1]})

@permission_required('ubuzima.can_view')
def view_indicator(req, indic, format = 'html'):
    filters = {'period':default_period(req),
             'location':default_location(req)}
    fld     = FieldType.objects.get(id = indic)
    pts     = matching_reports(req, filters).order_by('-created')[0:1]
    for p in range(0, len(pts)):
        if fld not in pts[p].fields.all()[0:1]: del pts[p]
    heads   = ['Reporter', 'Location', 'Patient', 'Type', 'Date']
    if format == 'csv':
        rsp = HttpResponse()
        rsp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(rsp, dialect = 'excel-tab')
        wrt.writerows([heads] +
        [[x.reporter.connection().identity, x.location, x.patient, x.type, x.created] for x in pts])
        return rsp
    return render_to_response(req, ('ubuzima/indicator.html'),
            {'headers': heads, 'patients':paginated(req, pts, prefix = 'ind')})

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

#   TODO: Error-prone list should be done in raw SQL. Later.
