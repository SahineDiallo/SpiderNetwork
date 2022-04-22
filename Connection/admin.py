from django.contrib import admin
from .models import ConnectionsList, ForgeLink


class ConnectionsListAdmin(admin.ModelAdmin):
    list_filter = ["user"]
    list_display = ["user"]
    search_fields = ["user"]
    read_only_fields = ["user"]

    class Meta:
        model = ConnectionsList


admin.site.register(ConnectionsList, ConnectionsListAdmin)


class ForgeLinkAdmin(admin.ModelAdmin):
    list_filter = ["sender", "receiver"]
    list_display = ["sender", "receiver"]
    search_fields = ["sender__email", "receiver__email",
                     "sender__username", "receiver__username", ]

    class Meta:
        model = ForgeLink


admin.site.register(ForgeLink, ForgeLinkAdmin)
