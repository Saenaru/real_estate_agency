from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Flat


class FlatAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'price',
        'town',
        'new_building',
        'construction_year'
    ]
    list_editable = ['new_building']
    search_fields = ['town', 'address', 'owner']
    list_filter = ['new_building', 'town', 'construction_year']
    readonly_fields = ['created_at']


admin.site.register(Flat, FlatAdmin)