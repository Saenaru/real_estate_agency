from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField


User = get_user_model()



class Flat(models.Model):
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

    def save(self, *args, **kwargs):
        if self.construction_year is not None:
            self.new_building = self.construction_year >= 2015
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Квартира'
        verbose_name_plural = 'Квартиры'




class Complaint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints',
        verbose_name='Кто жаловался'
    )
    flat = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        related_name='complaints_about',
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
    pure_phone = PhoneNumberField(
        'Номер владельца',
        blank=True,
        max_length=128,
        region='RU',
        null=True
    )
    flats = models.ManyToManyField(
        Flat,
        related_name='owners',
        verbose_name='Квартиры в собственности'
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Собственник'
        verbose_name_plural = 'Собственники'