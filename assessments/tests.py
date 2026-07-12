from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import ChildProfile
from assessments.models import Assessment


class AssessmentCreationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='parent',
            email='parent@example.com',
            password='secret123',
        )
        self.child = ChildProfile.objects.create(
            parent=self.user,
            name='Ava',
            date_of_birth=date(2022, 1, 10),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_can_create_assessment_with_selected_age(self):
        response = self.client.post(
            '/api/assessments/',
            {'child': self.child.id, 'age_at_assessment': 5},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        assessment = Assessment.objects.get(pk=response.json()['id'])
        self.assertEqual(assessment.age_at_assessment, 5)
