from typing import List

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


class AddMembersSerializer(serializers.Serializer):
    members_to_add = serializers.ListField(child=serializers.IntegerField())

    @staticmethod
    def validate_members_to_add(value: List[int]) -> List[int]:
        """
        Validate that the provided member PKs correspond to existing Person objects.
        """
        for member_pk in value:
            try:
                Person.objects.get(pk=member_pk)
            except Person.DoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid pk {member_pk} - object does not exist."
                )

        return value
