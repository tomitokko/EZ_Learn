from django.test import TestCase
from django.urls import reverse
from .models import Profile

# Create your tests here.
class LANGUAGE_CHOICES_TestCase(TestCase):
    def test_view_functionality(self):
        response = self.client.get(reverse('LANGUAGE_CHOICES'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expected list of language choices')

class COURSES_CHOICES_TestCase(TestCase):
    def test_view_functionality(self):
        response = self.client.get(reverse('COURSES_CHOICES'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expected list of course choices')
