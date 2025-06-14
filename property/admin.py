from django.contrib import admin

from .models import Flat


class FlatAdmin(admin.ModelAdmin):
    search_fields = [
        'town',
        'address',
        'owner'
    ]
    list_display = [
        'address',
        'price',
        'town',
        'owner'
    ]


admin.site.register(Flat, FlatAdmin)