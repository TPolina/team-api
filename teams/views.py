from typing import Type

from django.db.models import Count, QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer

from teams.models import Team, Person
from teams.serializers import (
    TeamSerializer,
    PersonSerializer,
    TeamListRetrieveSerializer,
)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.annotate(number_of_members=Count("members"))

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return TeamListRetrieveSerializer

        return TeamSerializer


class PersonViewSet(viewsets.ModelViewSet):
    # Can be also done in get_queryset depending on action
    queryset = Person.objects.prefetch_related("teams")
    serializer_class = PersonSerializer
