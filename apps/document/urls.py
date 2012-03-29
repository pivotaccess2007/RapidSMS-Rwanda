from django.conf.urls.defaults import patterns, include, url
from document.views import save_document, upload, doc_list

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^doc/$', save_document),
    url(r'^upload/$', upload),
    url(r'^list/$', doc_list),
    # url(r'^documentation/', include('documentation.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
