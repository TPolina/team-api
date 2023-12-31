from typing import Type

from django.db.models import Count, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from teams.models import Team, Person
from teams.serializers import (
    TeamSerializer,
    PersonSerializer,
    TeamListRetrieveSerializer,
    PersonListRetrieveSerializer,
    AddMembersSerializer,
    BasePersonSerializer,
    AddToTeamsSerializer,
)


class TeamViewSet(viewsets.ModelViewSet):
    # It is possible to add permissions
    # like IsAuthenticatedOrReadOnly or IsAdminOrReadOnly.
    # In this case, there are no permissions, as we assume
    # that this API will be used for internal company purposes
    # and will be available to everyone
    queryset = Team.objects.all()

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        # We perform annotation here to decrease the number of SQL queries
        if self.action in ("list", "retrieve"):
            queryset = queryset.annotate(number_of_members=Count("members"))

        return queryset

    def get_serializer_class(self) -> Type[Serializer] | None:
        if self.action in ("list", "retrieve"):
            return TeamListRetrieveSerializer

        if self.action in ("members", "specific_member"):
            return BasePersonSerializer

        if self.action == "add_members":
            return AddMembersSerializer

        return TeamSerializer

    @action(methods=["get"], detail=True, url_path="members", url_name="team-members")
    def members(self, request: Request, *args, **kwargs) -> Response:
        team = self.get_object()
        members = team.members.all()
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @members.mapping.put
    def add_members(self, request: Request, *args, **kwargs) -> Response:
        team = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            members_to_add = serializer.validated_data["members_to_add"]
            team.members.add(*members_to_add)
            team.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["get"],
        detail=True,
        url_path="members/(?P<person_id>[^/.]+)",
        url_name="team-specific-member",
    )
    def specific_member(
        self, request: Request, person_id: int, *args, **kwargs
    ) -> Response:
        team = self.get_object()
        member = get_object_or_404(team.members, pk=person_id)
        serializer = self.get_serializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @specific_member.mapping.delete
    def remove_specific_member(
        self, request: Request, person_id: int, *args, **kwargs
    ) -> Response:
        team = self.get_object()
        member = get_object_or_404(team.members, pk=person_id)
        team.members.remove(member)
        return Response(status=status.HTTP_200_OK)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        # Decrease the number of SQL queries
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("teams")

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return PersonListRetrieveSerializer

        if self.action in ("teams", "specific_team"):
            return TeamSerializer

        if self.action == "add_to_teams":
            return AddToTeamsSerializer

        return PersonSerializer

    @action(methods=["get"], detail=True, url_path="teams", url_name="person-teams")
    def teams(self, request: Request, *args, **kwargs) -> Response:
        person = self.get_object()
        teams = person.teams.all()
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @teams.mapping.put
    def add_to_teams(self, request: Request, *args, **kwargs) -> Response:
        person = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            teams = serializer.validated_data["teams"]
            person.teams.add(*teams)
            person.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["get"],
        detail=True,
        url_path="teams/(?P<team_id>[^/.]+)",
        url_name="person-specific-team",
    )
    def specific_team(
        self, request: Request, team_id: int, *args, **kwargs
    ) -> Response:
        person = self.get_object()
        team = get_object_or_404(person.teams, pk=team_id)
        serializer = self.get_serializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @specific_team.mapping.delete
    def remove_from_specific_team(
        self, request: Request, team_id: int, *args, **kwargs
    ) -> Response:
        person = self.get_object()
        team = get_object_or_404(person.teams, pk=team_id)
        person.teams.remove(team)
        return Response(status=status.HTTP_200_OK)
