"""
generated with djinit

API routes for clients app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'clients', views.ClientsViewSet)

# Get URL patterns
urlpatterns = router.urls
