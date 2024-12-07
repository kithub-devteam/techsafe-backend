from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, PartnershipCategoryViewSet, ActivitiesPartnerViewSet

router = DefaultRouter()
router.register(r'partners', PartnerViewSet)
router.register(r'partnership_categories', PartnershipCategoryViewSet)
router.register(r'activities_partners', ActivitiesPartnerViewSet)

urlpatterns = router.urls
