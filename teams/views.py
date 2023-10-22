from rest_framework import viewsets

from teams.models import Team, Person
from teams.serializers import TeamSerializer, PersonSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PersonViewSet(viewsets.ModelViewSet):
    # Can be also done in get_queryset depending on action
    queryset = Person.objects.prefetch_related("teams")
    serializer_class = PersonSerializer
