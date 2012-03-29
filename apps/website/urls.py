from django.conf.urls.defaults import *
#from website.views import test_display ,home , view_stats , view_ex, test_maker, save_document, upload, doc_list, contact, join, about, contact_us, news_filtered

import website.views as views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^tracking/', include('tracking.urls')),
    # Example:
    # (r'^phase2/', include('phase2.foo.urls')),
    #url(r'^home/$', test_display, name='home'),
    url(r'^home/$', views.home),
    #url(r'^map/$', view_stats),
    #url(r'^newmap/$', view_ex),
    #url(r'^test/$', test_maker),

    url(r'^home/register/$', views.register),
    url(r'^home/news_event/$', views.test_display),
    url(r'^home/news_event/(?P<comp_title>[^\.]+)/$', views.news_filtered),

    url(r'^home/join_us/$', views.join),
    url(r'^home/contact_us/$', views.contact),
    url(r'^home/thanking_contact/$', views.contact_us),
    url(r'^home/about_us/$', views.about),
    url(r'^home/partners/$', views.partners),

    url(r'^home/doc/$', views.save_document),
    url(r'^home/upload/$', views.upload),
    url(r'^home/list/$', views.doc_list),

    url(r'^home/faq/(?P<item_selected>[^\.]+)/$',views.faq_filtered),
    url(r'^home/frequent_questions/$',views.faq_retrieval),

    
)

