from typing import List, Type

from django.db.models import Model
from rest_framework import serializers

from teams.models import Team, Person


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name")


class TeamListRetrieveSerializer(TeamSerializer):
    number_of_members = serializers.IntegerField(read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ("number_of_members",)


class BasePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "email")


class PersonSerializer(BasePersonSerializer):
    class Meta(BasePersonSerializer.Meta):
        fields = BasePersonSerializer.Meta.fields + ("teams",)


class PersonListRetrieveSerializer(PersonSerializer):
    teams = TeamSerializer(many=True, read_only=True)


def validate_pks(value: List[int], model_class: Type[Model]) -> List[int]:
    """
    Validate that the provided PKs correspond to existing objects of a given model.
    """
    for pk in value:
        try:
            model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            raise serializers.ValidationError(
                f"Invalid pk {pk} - object does not exist."
            )

    return value


class AddMembersSerializer(serializers.Serializer):
    members_to_add = serializers.ListField(child=serializers.IntegerField())

    @staticmethod
    def validate_members_to_add(value: List[int]) -> List[int]:
        return validate_pks(value, Person)


class AddToTeamsSerializer(serializers.Serializer):
    teams = serializers.ListField(child=serializers.IntegerField())

    @staticmethod
    def validate_teams(value: List[int]) -> List[int]:
        return validate_pks(value, Team)
