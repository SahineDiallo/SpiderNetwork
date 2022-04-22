from django.contrib import admin
from .models import messages, singleOneToOneRoom, Connected

admin.site.register(messages)
admin.site.register(Connected)
# admin.site.register(Presence)
admin.site.register(singleOneToOneRoom)
