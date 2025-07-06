from django.db import migrations
from phonenumbers import parse, is_valid_number, NumberParseException
import re


def is_definitely_invalid(phone_str):
    """Определяет заведомо невалидные номера по шаблонам"""
    if not phone_str:
        return True
        
    clean_phone = re.sub(r'[^0-9]', '', str(phone_str))
    
    invalid_patterns = [
        r'^0+$',
        r'^123456',
        r'(\d)\1{5}',
        r'^555555',
        r'^999999'
    ]
    
    return any(re.search(pattern, clean_phone) for pattern in invalid_patterns)


def safe_fill_owner_pure_phone(apps, schema_editor):
    Flat = apps.get_model('property', 'Flat')
    
    for flat in Flat.objects.all().iterator(chunk_size=500):
        try:
            if not flat.owner_phone or is_definitely_invalid(flat.owner_phone):
                flat.owner_pure_phone = None
            else:
                try:
                    parsed = parse(str(flat.owner_phone), 'RU')
                    if is_valid_number(parsed):
                        if parsed.country_code == 7 and not str(parsed.national_number).startswith('0'):
                            flat.owner_pure_phone = flat.owner_phone
                        else:
                            flat.owner_pure_phone = None
                    else:
                        flat.owner_pure_phone = None
                except (NumberParseException, ValueError):
                    flat.owner_pure_phone = None
            
            Flat.objects.filter(pk=flat.pk).update(owner_pure_phone=flat.owner_pure_phone)
            
        except Exception as e:
            print(f"Ошибка при обработке квартиры {flat.id}: {str(e)}")
            Flat.objects.filter(pk=flat.pk).update(owner_pure_phone=None)


class Migration(migrations.Migration):
    dependencies = [
        ('property', '0008_add_owner_pure_phone'),
    ]

    operations = [
        migrations.RunPython(
            safe_fill_owner_pure_phone,
            lambda apps, schema_editor: apps.get_model('property', 'Flat')
                                       .objects.all()
                                       .update(owner_pure_phone=None)
        ),
    ]