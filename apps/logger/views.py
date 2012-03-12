
from rapidsms.webui.utils import render_to_response
from models import *
from datetime import datetime, timedelta
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.decorators import permission_required
from ubuzima.views import *

@permission_required('logger.can_view')
@require_http_methods(["GET"])
def index(req):
    filters = {'period':default_log_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)}
    template_name="logger/index.html"
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = Location.objects.get(id = lox)
        lxn=lxn.name+' '+lxn.type.name+', '+lxn.parent.parent.name+' '+lxn.parent.parent.type.name+', '+lxn.parent.parent.parent.name+' '+lxn.parent.parent.parent.type.name
    rez=Location.objects.filter(**match_logs(req,filters))
    incoming = IncomingMessage.objects.filter(**match_received(req,filters)).order_by('-received')
    outgoing = OutgoingMessage.objects.filter(**match_sent(req,filters)).order_by('-sent')
    all = []
    rezf=rez.filter(**match_logs_fresher(req))
    for msg in incoming: 
    	if p_location(msg.identity) in rezf: all.append(msg)
    for msg in outgoing: 
	if p_location(msg.identity) in rezf: all.append(msg)
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.date, x.date))
    if req.REQUEST.has_key('csv'):
    	htp = HttpResponse()
        htp['Content-Type'] = 'text/csv; encoding=%s' % (getdefaultencoding(),)
        wrt = csv.writer(htp, dialect = 'excel-tab')
        wrt.writerows([['DATE','REPORTER','BACKEND','LOCATION','MESSAGE']]+[[r.date, r.identity,r.backend,p_location(r.identity),r.text] for r in all])
                    
        return htp
    else:
	    return render_to_response(req, template_name, { "messages": paginated(req, all, prefix="rep"),'rez':len(rez),'rezf':len(rezf),'usrloc':UserLocation.objects.get(user=req.user),'start_date':date.strftime(filters['period']['start'], '%d.%m.%Y'),
		 'end_date':date.strftime(filters['period']['end'], '%d.%m.%Y'),'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1]
	    })

def match_received(req,diced,alllocs=False):
    rez={}
    try:
        rez['received__gte'] = diced['period']['start']
        rez['received__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass
    return rez
def match_sent(req,diced,alllocs=False):
    rez={}
    try:
        rez['sent__gte'] = diced['period']['start']
        rez['sent__lte'] = diced['period']['end']+timedelta(1)
    except KeyError:
        pass
    return rez

def match_logs(req,diced,alllocs=False):
    rez = {}
    pst = None
    
    try:
        if alllocs: raise KeyError
        loc = int(req.REQUEST['location'])
        rez['id'] = loc
    except KeyError:
        try:
            lox = LocationShorthand.objects.filter(district = int(req.REQUEST['district']))
            rez['id__in'] = [x.original.id for x in lox]
        except KeyError:
            try:
                lox = LocationShorthand.objects.filter(province = int(req.REQUEST['province']))
                rez['id__in'] = [x.original.id for x in lox]
            except KeyError:
                pass

    return rez

def match_logs_fresher(req):
    pst={}
    try:
        uloc=UserLocation.objects.get(user=req.user)
        if uloc and uloc.location.type.name=='Health Centre':
            loc=uloc.location.id
            pst['id'] = loc
        elif uloc and uloc.location.type.name=='District':   
            dst=uloc.location.id
            lox = LocationShorthand.objects.filter(district =dst )
            pst['id__in'] = [x.original.id for x in lox]
        elif uloc and uloc.location.type.name=='Province':
            prv=uloc.location.id  
            lox = LocationShorthand.objects.filter(province =prv )
            pst['id__in'] = [x.original.id for x in lox]

    except UserLocation.DoesNotExist:
        pass
    return pst

def p_location(no):
	
	location,reporter=None,None
	try:
		p=get_object_or_404(PersistantConnection, identity=no)
		r=get_object_or_404(Reporter, pk=p.reporter.pk)
		location=r.location
	except Exception:
		pass
	return location	
def default_log_period(req):
    if req.REQUEST.has_key('start_date') and req.REQUEST.has_key('end_date'):
        return {'start':cut_date(req.REQUEST['start_date']),
                  'end':cut_date(req.REQUEST['end_date'])}
    return {'start':date.today() - timedelta(1), 'end':date.today()}#In production
    #return {'start':date.today() - timedelta(date.today().day), 'end':date.today()}#locally
