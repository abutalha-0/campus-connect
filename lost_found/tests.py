from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import LostFoundItem, ClaimQuestion, ClaimAttempt, ClaimAnswer


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
        self.third_user = get_user_model().objects.create_user(
            email='charlie@example.com',
            username='charlie',
            full_name='Charlie Example',
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
            event_date='2026-07-20',
        )
        self.open_item = LostFoundItem.objects.create(
            user=self.user,
            title='Red laptop',
            description='Laptop found in engineering building',
            item_type='FOUND',
            category='Electronics',
            location='Engineering',
            status='OPEN',
            event_date='2026-07-22',
        )
        self.claimed_item = LostFoundItem.objects.create(
            user=self.other_user,
            title='Blue notebook',
            description='Notebook found in the cafeteria',
            item_type='FOUND',
            category='Books',
            location='Cafeteria',
            status='CLAIMED',
            event_date='2026-07-23',
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
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.open_item.refresh_from_db()
        self.assertEqual(self.open_item.status, 'CLOSED')
        self.assertIsNotNone(self.open_item.resolved_at)

    def test_serializer_privacy_hides_correct_answer_and_description_for_non_owner(self):
        question = ClaimQuestion.objects.create(
            item=self.open_item,
            question_text='What sticker is on the laptop?',
            correct_answer='Octocat sticker'
        )

        # Non-owner view
        self.client.force_authenticate(self.other_user)
        response = self.client.get(f'/api/lost-found/{self.open_item.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], '')  # Redacted description for FOUND item
        self.assertNotIn('correct_answer', response.data['claim_questions'][0])
        self.assertEqual(response.data['claim_questions'][0]['question_text'], 'What sticker is on the laptop?')

        # Owner view
        self.client.force_authenticate(self.user)
        owner_resp = self.client.get(f'/api/lost-found/{self.open_item.id}/')
        self.assertEqual(owner_resp.status_code, 200)
        self.assertEqual(owner_resp.data['description'], 'Laptop found in engineering building')
        self.assertEqual(owner_resp.data['claim_questions'][0]['correct_answer'], 'Octocat sticker')

    def test_claim_question_can_only_be_created_on_found_items_by_owner(self):
        # Non-owner attempts creation
        self.client.force_authenticate(self.other_user)
        resp = self.client.post(f'/api/lost-found/{self.open_item.id}/claim-questions/', {
            'question_text': 'What brand is it?',
            'correct_answer': 'Dell'
        }, format='json')
        self.assertEqual(resp.status_code, 403)

        # Owner attempts on LOST item
        self.client.force_authenticate(self.user)
        resp_lost = self.client.post(f'/api/lost-found/{self.closed_item.id}/claim-questions/', {
            'question_text': 'What color?',
            'correct_answer': 'Black'
        }, format='json')
        self.assertEqual(resp_lost.status_code, 400)

        # Owner creates on FOUND item
        resp_ok = self.client.post(f'/api/lost-found/{self.open_item.id}/claim-questions/', {
            'question_text': 'What brand is it?',
            'correct_answer': 'Dell'
        }, format='json')
        self.assertEqual(resp_ok.status_code, 201)
        self.assertEqual(ClaimQuestion.objects.filter(item=self.open_item).count(), 1)

    def test_claim_attempt_submission_validations(self):
        question = ClaimQuestion.objects.create(
            item=self.open_item,
            question_text='What sticker is on the laptop?',
            correct_answer='Octocat sticker'
        )

        # Owner cannot claim own item
        self.client.force_authenticate(self.user)
        resp_owner = self.client.post(f'/api/lost-found/{self.open_item.id}/claims/', {
            'answers': [{'question': question.id, 'answer_text': 'Octocat'}]
        }, format='json')
        self.assertEqual(resp_owner.status_code, 400)

        # Other user submits claim
        self.client.force_authenticate(self.other_user)
        resp_submit = self.client.post(f'/api/lost-found/{self.open_item.id}/claims/', {
            'answers': [{'question': question.id, 'answer_text': 'GitHub Octocat'}]
        }, format='json')
        self.assertEqual(resp_submit.status_code, 201)
        self.assertEqual(ClaimAttempt.objects.filter(item=self.open_item, claimant=self.other_user).count(), 1)

        # Duplicate attempt returns clean 400 error
        resp_dup = self.client.post(f'/api/lost-found/{self.open_item.id}/claims/', {
            'answers': [{'question': question.id, 'answer_text': 'GitHub Octocat'}]
        }, format='json')
        self.assertEqual(resp_dup.status_code, 400)
        self.assertIn('already submitted', resp_dup.data['detail'])

    def test_claim_attempt_approval_state_machine(self):
        question = ClaimQuestion.objects.create(
            item=self.open_item,
            question_text='What sticker is on the laptop?',
            correct_answer='Octocat'
        )

        # Bob submits attempt
        self.client.force_authenticate(self.other_user)
        bob_resp = self.client.post(f'/api/lost-found/{self.open_item.id}/claims/', {
            'answers': [{'question': question.id, 'answer_text': 'Octocat'}]
        }, format='json')
        bob_attempt_id = bob_resp.data['id']

        # Charlie submits attempt
        self.client.force_authenticate(self.third_user)
        charlie_resp = self.client.post(f'/api/lost-found/{self.open_item.id}/claims/', {
            'answers': [{'question': question.id, 'answer_text': 'Dog'}]
        }, format='json')
        charlie_attempt_id = charlie_resp.data['id']

        # Owner approves Bob's attempt
        self.client.force_authenticate(self.user)
        approve_resp = self.client.patch(f'/api/lost-found/claims/{bob_attempt_id}/', {
            'status': 'APPROVED'
        }, format='json')

        self.assertEqual(approve_resp.status_code, 200)
        self.assertEqual(approve_resp.data['status'], 'APPROVED')

        # Check item state
        self.open_item.refresh_from_db()
        self.assertEqual(self.open_item.status, 'CLAIMED')
        self.assertIsNotNone(self.open_item.resolved_at)

        # Check Charlie's attempt was auto-rejected
        charlie_attempt = ClaimAttempt.objects.get(id=charlie_attempt_id)
        self.assertEqual(charlie_attempt.status, 'REJECTED')
        self.assertIsNotNone(charlie_attempt.reviewed_at)

