from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Flat, Complaint, Owner

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

class OwnerThroughInline(admin.TabularInline):
    model = Owner.flats.through
    extra = 0
    raw_id_fields = ('owner',)
    verbose_name = _('Собственник')
    verbose_name_plural = _('Собственники')
    readonly_fields = ('owner_link', 'owner_phone', 'owner_pure_phone')
    fields = ('owner_link', 'owner_phone', 'owner_pure_phone')

    def owner_link(self, instance):
        owner = instance.owner
        url = reverse('admin:property_owner_change', args=[owner.id])
        return format_html('<a href="{}">{}</a>', url, owner.full_name)
    owner_link.short_description = _('ФИО')

    def owner_phone(self, instance):
        return instance.owner.phone
    owner_phone.short_description = _('Телефон')

    def owner_pure_phone(self, instance):
        return instance.owner.pure_phone
    owner_pure_phone.short_description = _('Нормализованный телефон')

@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'price',
        'town',
        'display_owner_phone',
        'display_pure_phone',
        'new_building',
        'display_likes_count',
        'construction_year',
        'display_complaints_count'
    ]
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'address',
                'price',
                'town',
                ('owner', 'owner_phone'),
                'new_building'
            ]
        }),
    ]
    list_editable = ['new_building']
    search_fields = ['town', 'address', 'owner']
    list_filter = ['new_building', 'town', 'construction_year']
    readonly_fields = ['created_at']
    inlines = [ComplaintInline, OwnerThroughInline]
    raw_id_fields = ['liked_by']  # Убрал 'owner' так как это не ForeignKey
    filter_horizontal = ('liked_by',)

    def display_complaints_count(self, obj):
        return obj.complaints.count()
    display_complaints_count.short_description = _('Количество жалоб')

    def display_likes_count(self, obj):
        return obj.liked_by.count()
    display_likes_count.short_description = _('Лайков')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('owners')

    def display_owner_phone(self, obj):
        return obj.owner_phone if obj.owner_phone else "-"
    display_owner_phone.short_description = 'Номер владельца'
    
    def display_pure_phone(self, obj):
        return obj.owner_pure_phone if obj.owner_pure_phone else "-"
    display_pure_phone.short_description = 'Нормализованный номер'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.save()

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
    raw_id_fields = ['user', 'flat']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = _('Текст жалобы')

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'display_phone', 'flats_count']
    search_fields = ['full_name', 'pure_phone']
    raw_id_fields = ['flats']
    fields = ['full_name', 'pure_phone', 'flats']
    
    def display_phone(self, obj):
        return obj.pure_phone.as_international if obj.pure_phone else "Не указан"
    display_phone.short_description = 'Номер владельца'
    
    def flats_count(self, obj):
        return obj.flats.count()
    flats_count.short_description = 'Количество квартир'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.save()