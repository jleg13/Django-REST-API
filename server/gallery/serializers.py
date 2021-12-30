from rest_framework import serializers

from core.models import Tag, GalleryItemBlurb


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class GalleryItemBlurbSerializer(serializers.ModelSerializer):
    """Serializer for gallery item blurb object"""

    class Meta:
        model = GalleryItemBlurb
        fields = ('id', 'blurb')
        read_only_fields = ('id',)
