from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import GalleryItem

from gallery.serializers import GalleryItemSerializer


GALLERY_ITEM_URL = reverse('gallery:galleryitem-list')


class PublicGalleryItemApiTests(TestCase):
    """Test the public gallery item API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving gallery item"""
        res = self.client.get(GALLERY_ITEM_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGalleryItemApiTests(TestCase):
    """Test the authorized user gallery item API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_gallery_item_(self):
        """Test retrieving gallery item list"""
        GalleryItem.objects.create(user=self.user,
                                   name='Item 1',
                                   blurb='Blurb 1')
        GalleryItem.objects.create(user=self.user,
                                   name='Item 2',
                                   blurb='Blurb 2')

        res = self.client.get(GALLERY_ITEM_URL)

        gallery_item = GalleryItem.objects.all().order_by('-name')
        serializer = GalleryItemSerializer(gallery_item, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_gallery_item_limited_to_user(self):
        """Test that gallery item returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@email.com',
            'testpass'
        )
        GalleryItem.objects.create(user=user2,
                                   name='Item 3',
                                   blurb='Blurb 3')

        gallery_item = GalleryItem.objects.create(user=self.user,
                                                  name='Item 4',
                                                  blurb='Burb 4')

        res = self.client.get(GALLERY_ITEM_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], gallery_item.name)

    def test_create_gallery_item_success(self):
        """Test creating a new gallery item"""
        payload = {'name': 'Item 5', 'blurb': 'Blurb 5'}
        self.client.post(GALLERY_ITEM_URL, payload)

        exists = GalleryItem.objects.filter(
            user=self.user,
            name=payload['name'],
            blurb=payload['blurb']
        ).exists()
        self.assertTrue(exists)

    def test_create_gallery_item_invalid(self):
        """Test creating a new gallery item with invalid payload"""
        payload = {'': ''}
        res = self.client.post(GALLERY_ITEM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)