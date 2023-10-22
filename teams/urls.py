from django.urls import path, include
from rest_framework import routers

from teams.views import TeamViewSet, PersonViewSet

router = routers.DefaultRouter()
router.register("teams", TeamViewSet)
router.register("people", PersonViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "teams"
