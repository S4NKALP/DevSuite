"""
generated with djinit

API routes for finance app.
"""

from rest_framework.routers import DefaultRouter
from . import views

# Create router instance
router = DefaultRouter()

# Register viewsets with router
# Example:
# router.register(r'finance', views.FinanceViewSet)

# Get URL patterns
urlpatterns = router.urls
