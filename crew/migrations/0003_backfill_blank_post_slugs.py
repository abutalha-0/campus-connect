from django.db import migrations
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    """Posts created before PostSerializer started deriving slug server-side
    (see 6679b5d) were saved with slug=''. Give each one a real slug so its
    detail/close/members/join-request URLs (all keyed on slug) work again.
    """
    Post = apps.get_model('crew', 'Post')
    for post in Post.objects.filter(slug=''):
        base = slugify(post.title)[:210] or 'post'
        slug = base
        suffix = 1
        while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
            suffix += 1
            slug = f'{base}-{suffix}'
        post.slug = slug
        post.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('crew', '0002_seed_categories'),
    ]

    operations = [
        migrations.RunPython(backfill_slugs, migrations.RunPython.noop),
    ]
