from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Gallery, Tag, GalleryItem
from gallery.serializers import GallerySerializer, GalleryDetailSerializer


GALLERY_URL = reverse('gallery:gallery-list')


def detail_url(gallery_id):
    """Return gallery detail URL"""
    return reverse('gallery:gallery-detail', args=[gallery_id])


def sample_tag(user, name='Pets'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_gallery_item(user, **params):
    """Create and return a sample gallery item"""
    defaults = {
        'name': 'Test gallery item',
        'blurb': 'Test blurb',
        'user': user
    }
    defaults.update(params)

    return GalleryItem.objects.create(**defaults)


def sample_gallery(user, **params):
    """Create and return a sample gallery"""
    defaults = {
        'title': 'Test gallery',
        'description': 'Test description',
        'user': user
    }
    defaults.update(params)

    return Gallery.objects.create(**defaults)


class PublicGalleryApiTests(TestCase):
    """Test the public gallery API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving galleries"""
        res = self.client.get(GALLERY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGalleryApiTests(TestCase):
    """Test the authorized user gallery API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_galleries(self):
        """Test retrieving galleries"""
        sample_gallery(user=self.user)
        sample_gallery(user=self.user)

        res = self.client.get(GALLERY_URL)

        galleries = Gallery.objects.all().order_by('-id')
        serializer = GallerySerializer(galleries, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_galleries_limited_to_user(self):
        """Test that galleries returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@email.com',
            'testpass'
        )
        sample_gallery(user=user2)
        sample_gallery(user=self.user)

        res = self.client.get(GALLERY_URL)

        galleries = Gallery.objects.filter(user=self.user)
        serializer = GallerySerializer(galleries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_gallery_detail(self):
        """Test viewing a gallery detail"""
        gallery = sample_gallery(user=self.user)
        gallery.tags.add(sample_tag(user=self.user))
        gallery.gallery_items.add(sample_gallery_item(user=self.user))

        url = detail_url(gallery.id)
        res = self.client.get(url)

        serializer = GalleryDetailSerializer(gallery)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
