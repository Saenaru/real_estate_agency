from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0009_safe_fill_owner_pure_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField('ФИО владельца', max_length=200)),
                ('phone', models.CharField('Номер владельца', max_length=20)),
                ('pure_phone', phonenumber_field.modelfields.PhoneNumberField(
                    'Нормализованный номер владельца',
                    blank=True,
                    max_length=128,
                    region='RU'
                )),
                ('flats', models.ManyToManyField(
                    related_name='owners',
                    to='property.Flat',
                    verbose_name='Квартиры в собственности'
                )),
            ],
            options={
                'verbose_name': 'Собственник',
                'verbose_name_plural': 'Собственники',
            },
        ),
    ]
