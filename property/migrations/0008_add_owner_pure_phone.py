from django.db import migrations
import phonenumber_field.modelfields

class Migration(migrations.Migration):

    dependencies = [
        ('property', '0007_auto_20250703_1351'), 
    ]

    operations = [
        migrations.AddField(
            model_name='flat',
            name='owner_pure_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                max_length=128,
                region='RU',
                verbose_name='Нормализованный номер владельца',
                null=True
            ),
        ),
    ]