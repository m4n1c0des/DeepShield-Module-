"""Tests for landing, registration, login and logout (Member 3)."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

PASSWORD = 'Str0ng!Pass_2026'


class PublicPages(TestCase):
    def test_pages_open(self):
        for name in ('home', 'login', 'register'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)


class Registration(TestCase):
    def data(self, **extra):
        return {'username': 'ali', 'email': 'ali@example.com', 'password1': PASSWORD, 'password2': PASSWORD, **extra}

    def test_register_creates_user_with_hashed_password(self):
        r = self.client.post(reverse('register'), self.data())
        self.assertRedirects(r, reverse('login'))
        user = User.objects.get(username='ali')
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_duplicate_email_rejected(self):
        User.objects.create_user('first', 'ali@example.com', PASSWORD)
        r = self.client.post(reverse('register'), self.data())
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='ali').exists())

    def test_password_mismatch_rejected(self):
        r = self.client.post(reverse('register'), self.data(password2='different'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='ali').exists())


class LoginLogout(TestCase):
    def setUp(self):
        User.objects.create_user('sara', 'sara@example.com', PASSWORD)

    def test_login_ok_then_logout(self):
        self.assertRedirects(self.client.post(reverse('login'), {'username': 'sara', 'password': PASSWORD}), reverse('dashboard'))
        self.assertContains(self.client.get(reverse('dashboard')), 'sara')
        self.assertRedirects(self.client.get(reverse('logout')), reverse('home'))

    def test_wrong_password(self):
        r = self.client.post(reverse('login'), {'username': 'sara', 'password': 'nope'})
        self.assertContains(r, 'Invalid username or password')

    def test_next_to_other_site_is_ignored(self):
        r = self.client.post(reverse('login') + '?next=https://evil.example/', {'username': 'sara', 'password': PASSWORD})
        self.assertRedirects(r, reverse('dashboard'))


class Dashboard(TestCase):
    def test_guest_is_sent_to_login(self):
        r = self.client.get(reverse('dashboard'))
        self.assertRedirects(r, reverse('login') + '?next=' + reverse('dashboard'))

    def test_logged_in_user_sees_their_details(self):
        User.objects.create_user('sara', 'sara@example.com', PASSWORD)
        self.client.login(username='sara', password=PASSWORD)
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'sara@example.com')
        self.assertContains(r, 'Welcome back')

    def test_login_with_next_goes_to_the_requested_page(self):
        User.objects.create_user('sara', 'sara@example.com', PASSWORD)
        r = self.client.post(reverse('login') + '?next=/dashboard/', {'username': 'sara', 'password': PASSWORD})
        self.assertRedirects(r, '/dashboard/')
