from django.urls import path, include
from rest_framework.routers import DefaultRouter

from gallery import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('gallery-items-blurb', views.GalleryItemBlurbViewSet)

app_name = 'gallery'

urlpatterns = [
    path('', include(router.urls))
]
