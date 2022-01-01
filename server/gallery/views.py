from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, GalleryItem, Gallery

from gallery import serializers


class BaseGalleryAttr(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin):
    """Base viewset for user owned gallery attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseGalleryAttr):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class GalleryItemViewSet(BaseGalleryAttr):
    """Manage gallery item in the database"""
    queryset = GalleryItem.objects.all()
    serializer_class = serializers.GalleryItemSerializer

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.GalleryItemSerializer
        elif self.action == 'upload_image':
            return serializers.GalleryItemImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a gallery item"""
        gallery_item = self.get_object()
        serializer = self.get_serializer(
            gallery_item,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class GalleryViewSet(viewsets.ModelViewSet):
    """Manage gallery in the database"""
    serializer_class = serializers.GallerySerializer
    queryset = Gallery.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.GalleryDetailSerializer

        return self.serializer_class
