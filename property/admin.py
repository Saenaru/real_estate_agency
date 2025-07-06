from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Flat, Complaint



class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 0
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    fields = ('user', 'text', 'created_at')
    verbose_name = _('Жалоба')
    verbose_name_plural = _('Жалобы')

class LikeInline(admin.TabularInline):
    model = Flat.liked_by.through
    extra = 1
    raw_id_fields = ('user',)
    verbose_name = _('Лайк')
    verbose_name_plural = _('Лайки')

@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'price',
        'town',
        'owner_phone',
        'new_building',
        'display_likes_count',
        'construction_year',
        'display_complaints_count'
    ]
    list_editable = ['new_building']
    search_fields = ['town', 'address', 'owner']
    list_filter = ['new_building', 'town', 'construction_year']
    readonly_fields = ['created_at']
    inlines = [ComplaintInline]
    raw_id_fields = ['liked_by']
    filter_horizontal = ('liked_by',)
    
    def display_complaints_count(self, obj):
        return obj.complaints.count()
    display_complaints_count.short_description = _('Количество жалоб')

    def display_likes_count(self, obj):
        return obj.liked_by.count()
    display_likes_count.short_description = _('Лайков')

    

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'flat',
        'truncated_text',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'user__username',
        'flat__address',
        'text'
    ]
    raw_id_fields = ['user', 'flat']  # Здесь правильно - оба поля являются ForeignKey
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = _('Текст жалобы')