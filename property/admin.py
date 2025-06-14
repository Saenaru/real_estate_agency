from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Flat


class FlatAdmin(admin.ModelAdmin):
    search_fields = ['town', 'address', 'owner']
    list_display = ['address', 'price', 'town', 'owner', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    fieldsets = [
        (None, {
            'fields': ['owner', 'owners_phonenumber']
        }),
        ('Информация о квартире', {
            'fields': ['description', 'price', 'town', 'town_district', 
                      'address', 'floor', 'rooms_number', 'living_area',
                      'has_balcony', 'active', 'construction_year']
        }),
        ('Метаданные', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]


admin.site.register(Flat, FlatAdmin)