from django.db import migrations

# Matches crew/validators.py CATEGORY_DETAIL_SCHEMAS keys.
CATEGORIES = [
    {'name': 'Study Partner', 'slug': 'study-partner', 'description': 'Find someone to study a course with.'},
    {'name': 'Contest Team', 'slug': 'contest-team', 'description': 'Form a team for a coding contest or hackathon.'},
    {'name': 'Travel Mate', 'slug': 'travel-mate', 'description': 'Find a travel companion.'},
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('crew', 'Category')
    for entry in CATEGORIES:
        Category.objects.get_or_create(slug=entry['slug'], defaults=entry)


def remove_categories(apps, schema_editor):
    Category = apps.get_model('crew', 'Category')
    Category.objects.filter(slug__in=[c['slug'] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crew', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
