from rest_framework.routers import DefaultRouter
from .views import GameViewSet, MoveViewSet
# ======================================================================================================================
router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'moves', MoveViewSet)
# ======================================================================================================================
urlpatterns = router.urls
# ======================================================================================================================