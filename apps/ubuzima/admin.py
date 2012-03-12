from django.contrib import admin
from apps.ubuzima.models import *

admin.site.register(Report)
admin.site.register(ReportType)
admin.site.register(Field)
admin.site.register(FieldType)
admin.site.register(Patient)
admin.site.register(ReminderType)
admin.site.register(Reminder)
admin.site.register(UserLocation)
admin.site.register(TriggeredAlert)

class TriggerAdmin(admin.ModelAdmin):
    pass

admin.site.register(TriggeredText, TriggerAdmin)



