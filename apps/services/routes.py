"""
generated with djinit

API routes for services app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'services', views.ServicesViewSet)

# Get URL patterns
urlpatterns = router.urls
