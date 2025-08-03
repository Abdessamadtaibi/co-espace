from rest_framework_nested import routers
from .views import CabinViewSet, RoomViewSet,CabinPsychologistViewSet,AppointmentViewSet

router = routers.DefaultRouter()
router.register(r'cabins', CabinViewSet, basename='cabin')
cabins_router = routers.NestedDefaultRouter(router, r'cabins', lookup='cabin')
cabins_router.register(r'rooms', RoomViewSet, basename='cabin-rooms')
cabins_router.register(r'psychologists', CabinPsychologistViewSet, basename='cabin-psychologists')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
urlpatterns = router.urls + cabins_router.urls