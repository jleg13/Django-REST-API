from rest_framework import serializers

from core.models import Tag, GalleryItem


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class GalleryItemSerializer(serializers.ModelSerializer):
    """Serializer for gallery item blurb object"""

    class Meta:
        model = GalleryItem
        fields = ('id', 'name', 'blurb')
        read_only_fields = ('id',)
