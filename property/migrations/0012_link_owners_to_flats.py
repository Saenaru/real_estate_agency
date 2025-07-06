from django.db import migrations

def link_owners_to_flats(apps, schema_editor):
    Flat = apps.get_model('property', 'Flat')
    Owner = apps.get_model('property', 'Owner')
    
    for flat in Flat.objects.all().iterator(chunk_size=500):
        owner = Owner.objects.filter(
            full_name=flat.owner,
            phone=str(flat.owner_phone) if flat.owner_phone else ''
        ).first()
        
        if owner:
            owner.flats.add(flat)
            if not owner.pure_phone and flat.owner_pure_phone:
                owner.pure_phone = flat.owner_pure_phone
                owner.save()

class Migration(migrations.Migration):
    dependencies = [
        ('property', '0011_migrate_owners'),
    ]

    operations = [
        migrations.RunPython(
            link_owners_to_flats,
            lambda apps, schema_editor: apps.get_model('property', 'Owner')
                                      .objects.all()
                                      .update(flats=[])
        ),
    ]