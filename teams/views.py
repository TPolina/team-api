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
)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

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
        url_name="team-specific_member",
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

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("teams")

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return PersonListRetrieveSerializer

        return PersonSerializer
