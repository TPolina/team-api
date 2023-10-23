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


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "email", "teams")


class PersonListRetrieveSerializer(PersonSerializer):
    teams = TeamSerializer(many=True, read_only=True)
