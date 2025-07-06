from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import format_number, PhoneNumberFormat, parse, is_valid_number, NumberParseException
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class Flat(models.Model):
    owner = models.CharField('ФИО владельца', max_length=200)
    owner_phone = PhoneNumberField(
        'Номер владельца',
        region='RU',
        blank=True,
        help_text='Номер в формате +7XXXXXXXXXX'
    )
    owner_pure_phone = PhoneNumberField(
    'Нормализованный номер владельца',
    region='RU',
    blank=True,
    null=True
    )
    created_at = models.DateTimeField(
        'Когда создано объявление',
        default=timezone.now,
        db_index=True
    )
    description = models.TextField('Текст объявления', blank=True)
    price = models.IntegerField('Цена квартиры', db_index=True)
    town = models.CharField(
        'Город, где находится квартира',
        max_length=50,
        db_index=True
    )
    town_district = models.CharField(
        'Район города, где находится квартира',
        max_length=50,
        blank=True,
        help_text='Чертаново Южное'
    )
    address = models.TextField(
        'Адрес квартиры',
        help_text='ул. Подольских курсантов д.5 кв.4'
    )
    floor = models.CharField(
        'Этаж',
        max_length=3,
        help_text='Первый этаж, последний этаж, пятый этаж'
    )
    rooms_number = models.IntegerField(
        'Количество комнат в квартире',
        db_index=True
    )
    living_area = models.IntegerField(
        'Количество жилых кв.метров',
        null=True,
        blank=True,
        db_index=True
    )
    has_balcony = models.NullBooleanField('Наличие балкона', db_index=True)
    active = models.BooleanField('Активно-ли объявление', db_index=True)
    construction_year = models.IntegerField(
        'Год постройки здания',
        null=True,
        blank=True,
        db_index=True
    )
    new_building = models.BooleanField(
        'Новостройка',
        null=True,
        blank=True,
        db_index=True
    )
    complaints = models.ManyToManyField(
        User,
        through='Complaint',
        related_name='complained_flats',
        verbose_name='Жалобы',
        blank=True
    )
    liked_by = models.ManyToManyField(
        User,
        related_name='liked_flats',
        verbose_name='Кто лайкнул',
        blank=True
    )

    def __str__(self):
        return f'{self.town}, {self.address} ({self.price}р.)'
    
    def clean(self):
        super().clean()
        if self.owner_phone:
            phone_str = str(self.owner_phone)
            
            if self.is_definitely_invalid(phone_str):
                raise ValidationError({
                    'owner_phone': 'Номер телефона содержит недопустимую последовательность цифр'
                })
                
            try:
                parsed = parse(phone_str, 'RU')
                if not is_valid_number(parsed):
                    raise ValidationError({
                        'owner_phone': 'Укажите корректный российский номер в формате +7XXXXXXXXXX'
                    })
            except NumberParseException:
                raise ValidationError({
                    'owner_phone': 'Неверный формат номера телефона'
                })

    @staticmethod
    def is_definitely_invalid(phone_str):
        """Определяет заведомо невалидные номера"""
        clean_phone = re.sub(r'[^0-9]', '', phone_str)
        
        invalid_patterns = [
            r'^0+$',
            r'^123456',
            r'(\d)\1{5}',
            r'^555555',
            r'^999999'
        ]
        
        return any(re.search(pattern, clean_phone) for pattern in invalid_patterns)

    def save(self, *args, **kwargs):
        self.full_clean()
        
        if self.owner_phone and not self.is_definitely_invalid(str(self.owner_phone)):
            try:
                parsed = parse(str(self.owner_phone), 'RU')
                if is_valid_number(parsed):
                    self.owner_pure_phone = self.owner_phone
                else:
                    self.owner_pure_phone = None
            except NumberParseException:
                self.owner_pure_phone = None
        else:
            self.owner_pure_phone = None
            
        super().save(*args, **kwargs)

    def clean(self):
        if self.owner_phone:
            if (self.owner_phone.country_code != 7 or 
                str(self.owner_phone.national_number).startswith('0')):
                raise ValidationError({
                    'owner_phone': 'Укажите корректный российский номер в формате +7XXXXXXXXXX'
                })
            
            if '000000' in str(self.owner_phone.national_number):
                raise ValidationError({
                    'owner_phone': 'Номер телефона содержит недопустимую последовательность цифр'
                })
            
    def get_formatted_phone(self):
        """Возвращает номер в формате +7 (XXX) XXX-XX-XX"""
        if not self.owner_phone:
            return ""
        return format_number(self.owner_phone, PhoneNumberFormat.INTERNATIONAL)
    
    get_formatted_phone.short_description = "Номер владельца"

    def save(self, *args, **kwargs):
        if self.construction_year is not None:
            self.new_building = self.construction_year >= 2015
        self.full_clean()
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.owner_phone:
            self.owner_pure_phone = self.owner_phone
        super().save(*args, **kwargs)


class Complaint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кто жаловался'
    )
    flat = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        verbose_name='Квартира, на которую пожаловались'
    )
    text = models.TextField(
        verbose_name='Текст жалобы',
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания жалобы'
    )

    def __str__(self):
        return f'Жалоба от {self.user} на квартиру {self.flat}'

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'

class Owner(models.Model):
    full_name = models.CharField('ФИО владельца', max_length=200)
    phone = models.CharField('Номер владельца', max_length=20)
    pure_phone = PhoneNumberField(
        'Нормализованный номер владельца',
        blank=True,
        max_length=128,
        region='RU'
    )
    flats = models.ManyToManyField(
        Flat,
        related_name='owners',
        verbose_name='Квартиры в собственности'
    )

    def __str__(self):
        return f'{self.full_name} ({self.phone})'

    class Meta:
        verbose_name = 'Собственник'
        verbose_name_plural = 'Собственники'
