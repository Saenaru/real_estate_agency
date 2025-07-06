from django.db import migrations

def migrate_owners(apps, schema_editor):
    Flat = apps.get_model('property', 'Flat')
    Owner = apps.get_model('property', 'Owner')
    
    for flat in Flat.objects.all().iterator(chunk_size=500):
        owner, created = Owner.objects.get_or_create(
            full_name=flat.owner,
            defaults={
                'phone': str(flat.owner_phone) if flat.owner_phone else '',
                'pure_phone': flat.owner_pure_phone if flat.owner_pure_phone else '',
            }
        )
        owner.flats.add(flat)

class Migration(migrations.Migration):
    dependencies = [
        ('property', '0010_owner'),
    ]

    operations = [
        migrations.RunPython(
            migrate_owners,
            lambda apps, schema_editor: apps.get_model('property', 'Owner').objects.all().delete()
        ),
    ]