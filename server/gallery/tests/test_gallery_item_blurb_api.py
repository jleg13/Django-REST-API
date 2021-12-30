from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import GalleryItemBlurb

from gallery.serializers import GalleryItemBlurbSerializer


GALLERY_ITEM_BLURB_URL = reverse('gallery:galleryitemblurb-list')


class PublicGalleryItemBlurbApiTests(TestCase):
    """Test the public gallery item blurb API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving gallery item blurb"""
        res = self.client.get(GALLERY_ITEM_BLURB_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGalleryItemBlurbApiTests(TestCase):
    """Test the authorized user gallery item blurb API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_gallery_item_blurb(self):
        """Test retrieving gallery item blurb list"""
        GalleryItemBlurb.objects.create(user=self.user,
                                        blurb='This is blurb 1')
        GalleryItemBlurb.objects.create(user=self.user,
                                        blurb='This is blurb 2')

        res = self.client.get(GALLERY_ITEM_BLURB_URL)

        gallery_item_blurbs = GalleryItemBlurb.objects.all().order_by('-blurb')
        serializer = GalleryItemBlurbSerializer(gallery_item_blurbs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_gallery_item_blurb_limited_to_user(self):
        """Test that gallery item blurb returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@email.com',
            'testpass'
        )
        GalleryItemBlurb.objects.create(user=user2,
                                        blurb='This is blurb 3')

        gallery_item_blurb = GalleryItemBlurb.objects.create(
            user=self.user, blurb='This is blurb 4')

        res = self.client.get(GALLERY_ITEM_BLURB_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['blurb'], gallery_item_blurb.blurb)
