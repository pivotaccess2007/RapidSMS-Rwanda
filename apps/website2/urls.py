from django.conf.urls.defaults import *
from website.views import test_display ,home , view_stats , view_ex, test_maker, save_document, upload, doc_list, contact, join, about, contact_us, news_filtered

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^phase2/', include('phase2.foo.urls')),
    url(r'^home/$', test_display, name='home'),
    url(r'^home/$', home, name='test'),
    url(r'^map/$', view_stats),
    url(r'^newmap/$', view_ex),
    url(r'^test/$', test_maker),

    
    url(r'^news_event/$', test_display),
    url(r'^news_event/(?P<comp_title>[^\.]+)/$', news_filtered),

    url(r'^join_us/$', join),
    url(r'^contact_us/$', contact),
    url(r'^thanking_contact/$', contact_us),
    url(r'^about_us/$', about),

    url(r'^doc/$', save_document),
    url(r'^upload/$', upload),
    url(r'^list/$', doc_list),

    
)

