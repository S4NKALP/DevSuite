"""
generated with djinit

API routes for core app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'core', views.CoreViewSet)

# Get URL patterns
urlpatterns = router.urls
