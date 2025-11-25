"""
generated with djinit

API routes for notifications app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'notifications', views.NotificationsViewSet)

# Get URL patterns
urlpatterns = router.urls
