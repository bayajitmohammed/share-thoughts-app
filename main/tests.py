from django.contrib.auth.models import User
from django.test import TestCase, override_settings


class ProductionPasswordResetTests(TestCase):
    @override_settings(DEBUG=False)
    def test_anonymous_reset_cannot_change_password(self):
        user = User.objects.create_user(username='alice', password='original-password')
        response = self.client.post('/forgot-password/', {
            'identifier': 'alice', 'new_password': 'attacker-password',
        })
        self.assertEqual(response.status_code, 404)
        user.refresh_from_db()
        self.assertTrue(user.check_password('original-password'))
