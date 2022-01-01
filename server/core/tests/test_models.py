from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@email.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_succesful(self):
        """"Test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, 'password123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.com', 'password123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_gallery_item_str(self):
        """Test the gallery item string representation"""
        gallery_item = models.GalleryItem.objects.create(
            user=sample_user(),
            name='Test gallery item',
            blurb='This is a blurb'
        )

        self.assertEqual(str(gallery_item), gallery_item.name)

    def test_gallery_str(self):
        """Test the gallery string representation"""
        gallery = models.Gallery.objects.create(
            user=sample_user(),
            title='Test gallery',
            description='This is a description'
        )

        self.assertEqual(str(gallery), gallery.title)

    @patch('uuid.uuid4')
    def test_gallery_item_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.gallery_item_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/gallery-items/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
