from django.test import TestCase
from django.contrib.auth import get_user_model

class CustomUserTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='testuser@gmail.com', username='testuser', password='testpass123')
        self.assertEqual(user.email, 'testuser@gmail.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser) 
    
    def test_create_superuser(self):
        User = get_user_model()
        superuser = User.objects.create_superuser(email='testsuperuser@gmail.com', username='testsuperuser', password='testpass123')
        self.assertEqual(superuser.email, 'testsuperuser@gmail.com')
        self.assertEqual(superuser.username, 'testsuperuser')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)     