# Create your views here.
# Create your views here.

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext,Context
from django.shortcuts import render_to_response
#from rapidsms.webui.utils import render_to_response
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.core.files import File
from operator import itemgetter, attrgetter
import datetime
from cStringIO import StringIO
from models import *
from django.contrib.auth.models import *
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from rapidsms.webui.utils import *


@permission_required('website.can_view')
@csrf_exempt
def home(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('website/index.html',my_rc)


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
         
            event=Document_identification.objects.all().order_by("-id")
            paginator = Paginator(event, 3)

            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
   
            try:
                docs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                docs = paginator.page(paginator.num_pages)


            my_rc=RequestContext(request,({'docs':docs}))
            return render_to_response('website/list_doc.html', my_rc)

        else:
            my_rc=RequestContext(request,({'errors': errors}))
            return render_to_response('website/save_doc.html', my_rc)

    else:
        event=Document_identification.objects.all().order_by("-id")
    
        paginator = Paginator(event, 3)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
   
        try:
            docs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            docs = paginator.page(paginator.num_pages)


        my_rc=RequestContext(request,({'docs':docs}))
        return render_to_response('website/list_doc.html', my_rc)

@csrf_exempt
def upload(request):
    form=['amazi']
    my_rc=RequestContext(request,({'form':form}))
    return render_to_response('website/save_doc.html', my_rc)

@csrf_exempt
def doc_list(request):
    event=Document_identification.objects.all().order_by("-id")
    
    paginator = Paginator(event, 3)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
   
    try:
        docs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        docs = paginator.page(paginator.num_pages)


    my_rc=RequestContext(request,({'docs':docs}))
    return render_to_response('website/list_doc.html', my_rc)

@csrf_exempt
def test_display(request):
    now =datetime.datetime.now()
    date_now =now.strftime("%Y-%m-%d %H:%M:%S")
    comt=News_and_Event.objects.all()
    event=sorted(comt,key=attrgetter('date_created'), reverse=True)[:3]
    my_rc=RequestContext(request,({'news_and_event':event}))
    return render_to_response('website/news_event.html',my_rc)


@csrf_exempt
def contact(request):
    contacted_people=ContactMessage.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")[:3]
    my_rc=RequestContext(request,({'contacted_people':contacted_people}))
    return render_to_response('website/contact_us.html',my_rc)

@csrf_exempt
def join(request):
    users=Join_us.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")
    my_rc=RequestContext(request,({'users':users}))
    return render_to_response('website/join_us.html',my_rc)

@csrf_exempt
def about(request):
    items=About_us_info.objects.all().order_by("-id")
    my_rc=RequestContext(request,({'items':items}))
    return render_to_response('website/about_us.html',my_rc)

@csrf_exempt
def faq_retrieval(request):
    items=Faq.objects.all()
    my_rc=RequestContext(request,({'items':items}))
    return render_to_response('website/faq_list.html',my_rc)

@csrf_exempt
def faq_filtered(request,item_selected):
    item_s=Faq.objects.filter(id=item_selected)
    items=Faq.objects.all()
    my_rc=RequestContext(request,({'item_sel':item_s,'list':items}))
    return render_to_response('website/faq_list.html',my_rc) 

@csrf_exempt
def partners(request):
    evt='amazi'
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('website/partners.html',my_rc)
 

# **flts
@csrf_exempt
def view_stats(req):
    evt='amazi'
    my_rc=RequestContext(req,({'news_event':evt}))
    return render_to_response('website/example.html',my_rc)


@csrf_exempt
def view_ex(req):
    evt='amazi'
    saved_data=Location.objects.all().order_by("-id")
    my_rc=RequestContext(req,({'news_event':evt,'test':saved_data}))
    return render_to_response('website/newmap.html',my_rc)

@csrf_exempt
def test_maker(req):
    evt='amazi'
    saved_data=Location.objects.all().order_by("-id")
    my_rc=RequestContext(req,({'news_event':evt,'test':saved_data}))
    return render_to_response('website/test_makers.html',my_rc)


@csrf_exempt
def news_filtered(request,comp_title):
    evt=News_and_Event.objects.filter(id=comp_title)
    my_rc=RequestContext(request,({'news_event':evt}))
    return render_to_response('website/news_event_filtered.html',my_rc)


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
                contacted_people=ContactMessage.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")[:3]
                my_rc=RequestContext(request,({'contacted_people':contacted_people}))
                return render_to_response('website/contact_thank.html',my_rc)
                
#return HttpResponseRedirect('/contact/thanks/')
        else:
            my_rc=RequestContext(request,({
                "errors": errors,
                "subject": request.POST.get('subject', ''),
                "message": request.POST.get('message_ent', ''),
                "phone": request.POST.get('telnumber', ''),
                "name_send": request.POST.get('name_sd', ''),
            }))
            return render_to_response('website/contact_us.html', my_rc)
        
    else:
        contacted_people=ContactMessage.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")[:3]
        my_rc=RequestContext(request,({'contacted_people':contacted_people}))
        return render_to_response('website/contact_us.html',my_rc)




@csrf_exempt
def register(request):
        
    errors=[]
    if request.method == 'POST':
        name = request.POST.get('your_name')
        username = request.POST.get('your_username')
        email = request.POST.get('your_email')
        phone_number = request.POST.get('phone')
        

        if not request.POST.get('your_name'):
            errors.append('Enter a name.')

        if not request.POST.get('your_username'):
            errors.append('Enter a username.')

        if not request.POST.get('your_email') or '@' not in request.POST['your_email']:
            errors.append('Enter a valid e-mail address.')
            
        if not request.POST.get('phone'):
            errors.append('Enter a phone number.')

            
        if Join_us.objects.filter(username=username):
            errors.append('Username already existing in the database.')



        if not errors:                        
            test=Join_us(full_name = name,username = username,email=email,phone_number=phone_number)
            test.save()
            
            
            users=Join_us.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")
            my_rc=RequestContext(request,({'users':users}))
            return render_to_response('website/join_thank.html', my_rc)

                
        else:
            my_rc=RequestContext(request,({
                'errors':errors,
                'your_name': request.POST.get('your_name', ''),
                'your_username': request.POST.get('your_username', ''),
                'your_email': request.POST.get('your_email', ''),
                'phone': request.POST.get('phone', ''),
                
            }))
            return render_to_response('website/join_us.html', my_rc)
    else:
        users=Join_us.objects.all().extra(where=['approved = %s'], params=['Yes']).order_by("-id")
        my_rc=RequestContext(request,({'users':users}))
        return render_to_response('website/join_us.html', my_rc)


