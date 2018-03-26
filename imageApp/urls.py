from rest_framework.routers import DefaultRouter
from imageApp import views
from django.conf.urls import url,include

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'read-image', views.ImageComponents,base_name='read-image')

urlpatterns = [
    url(r'^', include(router.urls)),
]


