from django.contrib import admin

from models import Config, ReceivedFile, Event
from solo.admin import SingletonModelAdmin


class ReceivedFileAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'server', 'collection', 'filename')


class EventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'server', 'collection', 'operation', 'contents')


admin.site.register(Config, SingletonModelAdmin)
admin.site.register(ReceivedFile, ReceivedFileAdmin)
admin.site.register(Event, EventAdmin)
