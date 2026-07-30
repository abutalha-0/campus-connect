from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Route, RouteJoinRequest

User = get_user_model()


class RouteMateTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            full_name='User One',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            full_name='User Two',
            password='password123'
        )

        self.client.force_authenticate(user=self.user1)

        self.route1 = Route.objects.create(
            owner=self.user1,
            home_area='Agargaon',
            destination='Main Gate',
            days_active='Sun,Mon,Tue,Wed,Thu',
            transport_mode='Rickshaw',
            gender_preference='ANY',
            contact_info='01700000000'
        )

    def test_create_route(self):
        url = reverse('route-list')
        data = {
            'home_area': 'Mirpur 10',
            'destination': 'Campus Library',
            'days_active': 'Sun,Tue,Thu',
            'transport_mode': 'Bus',
            'gender_preference': 'FEMALE_ONLY',
            'contact_info': '01800000000'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['home_area'], 'Mirpur 10')
        self.assertEqual(response.data['owner_username'], 'user1')

    def test_list_and_filter_routes(self):
        url = reverse('route-list')
        response = self.client.get(url, {'home_area': 'Agargaon'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Contact info should be visible for owner
        self.assertEqual(response.data[0]['contact_info'], '01700000000')

        # Switch to user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url, {'home_area': 'Agargaon'})
        # Contact info should be masked for non-owner without accepted request
        self.assertEqual(response.data[0]['contact_info'], '[Contact info locked until request is accepted]')

    def test_join_request_flow_and_contact_unlock(self):
        # User2 requests to join User1's route
        self.client.force_authenticate(user=self.user2)
        request_url = reverse('route-join-request-create', kwargs={'pk': self.route1.id})
        data = {
            'note': 'Can I join your rickshaw ride?',
            'requester_contact_info': '01900000000'
        }
        response = self.client.post(request_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_id = response.data['id']

        # User1 views requests
        self.client.force_authenticate(user=self.user1)
        list_req_url = reverse('route-join-request-list', kwargs={'pk': self.route1.id})
        response = self.client.get(list_req_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # User1 accepts the request
        respond_url = reverse('route-request-respond', kwargs={'pk': request_id})
        response = self.client.post(respond_url, {'action': 'ACCEPT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ACCEPTED')

        # User2 views route detail again - contact_info is now unlocked!
        self.client.force_authenticate(user=self.user2)
        detail_url = reverse('route-detail', kwargs={'pk': self.route1.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contact_info'], '01700000000')

    def test_pause_and_close_route(self):
        detail_url = reverse('route-detail', kwargs={'pk': self.route1.id})
        response = self.client.patch(detail_url, {'status': 'PAUSED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PAUSED')

    def test_my_routes_and_history(self):
        my_routes_url = reverse('my-routes')
        response = self.client.get(my_routes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['posted_routes']), 1)

        history_url = reverse('route-history')
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
