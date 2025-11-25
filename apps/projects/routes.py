"""
generated with djinit

API routes for projects app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'projects', views.ProjectsViewSet)

# Get URL patterns
urlpatterns = router.urls
