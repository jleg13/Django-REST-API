from rest_framework import serializers

from core.models import Tag, GalleryItem, Gallery


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


class GallerySerializer(serializers.ModelSerializer):
    """Serializer for gallery object"""
    gallery_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=GalleryItem.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=GalleryItem.objects.all()
    )

    class Meta:
        model = Gallery
        fields = ('id', 'title', 'description', 'gallery_items', 'tags')
        read_only_fields = ('id',)


class GalleryDetailSerializer(GallerySerializer):
    """Serializer for gallery object with detail"""
    gallery_items = GalleryItemSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
