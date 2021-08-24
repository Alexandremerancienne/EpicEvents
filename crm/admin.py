from django.contrib import admin

from .models import Client, Contract, Event, Note

admin.site.register(Client)
admin.site.register(Contract)
admin.site.register(Note)
admin.site.register(Event)
