from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AccountsTestCase(TestCase):
    """Test accounts app"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass@123'
        )

    def test_signup_page_loads(self):
        """Signup page khul raha hai?"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_login_page_loads(self):
        """Login page khul raha hai?"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_signup_creates_user(self):
        """Signup se user ban raha hai?"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass@123',
            'password2': 'ComplexPass@123',
        })
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_signup_password_mismatch(self):
        """Password mismatch par user nahi banna chahiye"""
        response = self.client.post(reverse('signup'), {
            'username': 'baduser',
            'password1': 'Pass@12345',
            'password2': 'DifferentPass@123',
        })
        self.assertEqual(User.objects.filter(username='baduser').count(), 0)

    def test_login_valid_credentials(self):
        """Valid credentials se login ho raha hai?"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        """Galat password se login nahi hona chahiye"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        # Form error ke saath re-render hoga, redirect nahi
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects(self):
        """Logout ke baad login page par bhej raha hai?"""
        self.client.login(username='testuser', password='TestPass@123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)