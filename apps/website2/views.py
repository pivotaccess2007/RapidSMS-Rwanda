# Create your views here.
# Create your views here.

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext,Context
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.core.files import File
from operator import itemgetter, attrgetter
import datetime
from cStringIO import StringIO
from models import Document_identification, News_and_Event, ContactMessage, Location

@csrf_exempt
def save_document(request):
    errors = []
    if request.method == 'POST':
        name = request.FILES['document']
            
        if not request.POST.get('name_doc'):
            errors.append('Enter a name.')
            
        if not request.POST.get('doc_descr'):
            errors.append('Enter a name.')

        if not request.FILES['document']:
            errors.append('Browse the doc.')

            
        if not errors:
            name_doc=request.POST.get('name_doc')
            descr=request.POST.get('doc_descr')
            doc=request.FILES['document']

            save_document=Document_identification(name=name_doc,description=descr,document_name=doc)
            save_document.save()
         
            docs=Document_identification.objects.all()
            my_rc=RequestContext(request,({'docs': docs}))
            return render_to_response('/website/list_doc.html', my_rc)

        else:
            my_rc=RequestContext(request,({'errors': errors}))
            return render_to_response('/website/save_doc.html', my_rc)

    else:
        docs=Document_identification.objects.all()
        my_rc=RequestContext(request,({'docs':docs}))
        return render_to_response('/website/list_doc.html', my_rc)

@csrf_exempt
def upload(request):
    form=['amazi']
    my_rc=RequestContext(request,({'form':form}))
    return render_to_response('save_doc.html', my_rc)

@csrf_exempt
def doc_list(request):
    docs=Document_identification.objects.all()
    my_rc=RequestContext(request,({'docs':docs}))
    return render_to_response('list_doc.html', my_rc)

@csrf_exempt
def test_display(request):
    now =datetime.datetime.now()
    date_now =now.strftime("%Y-%m-%d %H:%M:%S")
    comt=News_and_Event.objects.all()
    event=sorted(comt,key=attrgetter('date_created'), reverse=True)[:3]
    my_rc=RequestContext(request,({'news_and_event':event}))
    return render_to_response('website/news_event.html',my_rc)

@csrf_exempt
def home(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('index.html',my_rc)

@csrf_exempt
def contact(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('contact_us.html',my_rc)

@csrf_exempt
def join(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('join_us.html',my_rc)

@csrf_exempt
def about(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('about_us.html',my_rc)


# **flts
@csrf_exempt
def view_stats(req):
    evt='amazi'
    my_rc=RequestContext(req,({'news_event':evt}))
    return render_to_response('example.html',my_rc)


@csrf_exempt
def view_ex(req):
    evt='amazi'
    saved_data=Location.objects.all().order_by("-id")
    my_rc=RequestContext(req,({'news_event':evt,'test':saved_data}))
    return render_to_response('newmap.html',my_rc)

@csrf_exempt
def test_maker(req):
    evt='amazi'
    saved_data=Location.objects.all().order_by("-id")
    my_rc=RequestContext(req,({'news_event':evt,'test':saved_data}))
    return render_to_response('test_makers.html',my_rc)


@csrf_exempt
def news_filtered(request,comp_title):
    evt=News_and_Event.objects.filter(title_name=comp_title)
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('news_event_filtered.html',my_rc)


@csrf_exempt	
def contact_us(request):
    errors = []
    if request.method == 'POST'and request.POST is not None:
        if not request.POST.get('name_sd'):
            errors.append('Enter your name.')

        if not request.POST.get('subject', ''):
            errors.append('Enter a subject.')

        if not request.POST.get('message_ent',''):
            errors.append('Enter your message.')


        if not errors:
            now = datetime.datetime.now()
            name_sender = request.POST.get('name_sd')
            tel_sender = request.POST.get('telnumber')
            subject_sender=request.POST.get('subject')
            message_sender=request.POST.get('message_ent')
            time_sender=now.strftime("%Y-%m-%d %H:%M")

            try:
                kist = ContactMessage.objects.get(name_sender = name_sender,subject=subject_sender,message=message_sender)
                
            except: 
                contact_msg=ContactMessage(name_sender = name_sender,tel_sender=tel_sender,subject=subject_sender,message=message_sender,date_rec=time_sender)
                contact_msg.save()
                evt='amazi'
                my_rc=RequestContext(request,({'news_event':evt}))
                return render_to_response('contact_thank.html',my_rc)
                
#return HttpResponseRedirect('/contact/thanks/')
        else:
            my_rc=RequestContext(request,({
                "errors": errors,
                "subject": request.POST.get('subject', ''),
                "message": request.POST.get('message_ent', ''),
                "phone": request.POST.get('telnumber', ''),
                "name_send": request.POST.get('name_sd', ''),
            }))
            return render_to_response('contact_us.html', my_rc)
        
    else:
        evt='amazi'
        my_rc=RequestContext(request,({'news_event':evt}))
        return render_to_response('contact_us.html',my_rc)


