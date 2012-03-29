from django.contrib import admin
from website.models import News_and_Event, Document_identification, ContactMessage, Location


admin.site.register( News_and_Event )
admin.site.register( Document_identification )
admin.site.register( ContactMessage )
admin.site.register( Location )
