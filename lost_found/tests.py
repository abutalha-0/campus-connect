from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import LostFoundItem


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class LostFoundItemAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='alice@example.com',
            username='alice',
            full_name='Alice Example',
            password='password123',
        )
        self.other_user = get_user_model().objects.create_user(
            email='bob@example.com',
            username='bob',
            full_name='Bob Example',
            password='password123',
        )

        self.closed_item = LostFoundItem.objects.create(
            user=self.user,
            title='Black wallet',
            description='Wallet lost near the library',
            item_type='LOST',
            category='ID card',
            location='Library',
            status='CLOSED',
            date_seen='2026-07-20',
        )
        self.open_item = LostFoundItem.objects.create(
            user=self.user,
            title='Red laptop',
            description='Laptop found in engineering building',
            item_type='FOUND',
            category='Electronics',
            location='Engineering',
            status='OPEN',
            date_seen='2026-07-22',
        )
        self.claimed_item = LostFoundItem.objects.create(
            user=self.other_user,
            title='Blue notebook',
            description='Notebook found in the cafeteria',
            item_type='FOUND',
            category='Books',
            location='Cafeteria',
            status='CLAIMED',
            date_seen='2026-07-23',
        )

    def test_list_excludes_closed_posts_by_default_and_filters_by_category_location_status_and_date(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            '/api/lost-found/?category=Electronics&location=Engineering&status=open&date=2026-07-22'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Red laptop')

    def test_my_posts_endpoint_returns_only_the_current_users_posts(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/lost-found/my-posts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all(item['reported_by'] == 'alice' for item in response.data))

    def test_owner_can_close_a_post(self):
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f'/api/lost-found/{self.open_item.id}/',
            {'status': 'CLOSED'},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200)
        self.open_item.refresh_from_db()
        self.assertEqual(self.open_item.status, 'CLOSED')
