"""
generated with djinit

API routes for productivity app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'productivity', views.ProductivityViewSet)

# Get URL patterns
urlpatterns = router.urls
