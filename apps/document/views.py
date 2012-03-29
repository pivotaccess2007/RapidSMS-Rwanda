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
from models import Document_identification

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
            return render_to_response('list_doc.html', my_rc)

        else:
            my_rc=RequestContext(request,({'errors': errors}))
            return render_to_response('save_doc.html', my_rc)

    else:
        docs=Document_identification.objects.all()
        my_rc=RequestContext(request,({'docs':docs}))
        return render_to_response('list_doc.html', my_rc)

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
