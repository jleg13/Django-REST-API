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


def sample_tag(user, **params):
    """Create and return a sample tag"""
    defaults = {
        'name': 'Test tag',
        'user': user
    }
    defaults.update(params)

    return Tag.objects.create(**defaults)


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

    def test_create_basic_gallery_(self):
        """Test creating a new gallery"""
        payload = {
            'title': 'Test gallery',
            'description': 'Test description'
        }
        res = self.client.post(GALLERY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        gallery = Gallery.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(gallery, key))

    def test_create_gallery_with_tags(self):
        """Test creating a gallery with tags"""
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user)
        payload = {
            'title': 'Test gallery',
            'description': 'Test description',
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(GALLERY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        gallery = Gallery.objects.get(id=res.data['id'])
        tags = gallery.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_gallery_with_gallery_items(self):
        """Test creating a gallery with gallery items"""
        gallery_item1 = sample_gallery_item(user=self.user)
        gallery_item2 = sample_gallery_item(user=self.user)
        payload = {
            'title': 'Test gallery',
            'description': 'Test description',
            'gallery_items': [gallery_item1.id, gallery_item2.id]
        }
        res = self.client.post(GALLERY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        gallery = Gallery.objects.get(id=res.data['id'])
        gallery_items = gallery.gallery_items.all()
        self.assertEqual(gallery_items.count(), 2)
        self.assertIn(gallery_item1, gallery_items)
        self.assertIn(gallery_item2, gallery_items)

    def test_partial_update_gallery(self):
        """Test updating a gallery with patch"""
        gallery = sample_gallery(user=self.user)
        gallery.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Test tag 2')
        payload = {
            'title': 'New title',
            'description': 'New description',
            'tags': [new_tag.id]
        }
        url = detail_url(gallery.id)
        self.client.patch(url, payload)

        gallery.refresh_from_db()
        self.assertEqual(gallery.title, payload['title'])
        self.assertEqual(gallery.description, payload['description'])
        tags = gallery.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_gallery(self):
        """Test updating a gallery with put"""
        gallery = sample_gallery(user=self.user)
        gallery.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'New title',
            'description': 'New description',
        }
        url = detail_url(gallery.id)
        self.client.put(url, payload)

        gallery.refresh_from_db()
        self.assertEqual(gallery.title, payload['title'])
        self.assertEqual(gallery.description, payload['description'])
        tags = gallery.tags.all()
        self.assertEqual(len(tags), 0)
