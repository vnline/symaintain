__author__ = 'vnline'

from models import Schedule,Hotfile,Deploy,Operation
from django.contrib import admin

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('agent', 'server_name', 'open_time', 'version')
    list_filter = ('open_time',)
    date_hierarchy = 'open_time'

admin.site.register(Schedule,ScheduleAdmin)
admin.site.register(Hotfile)

