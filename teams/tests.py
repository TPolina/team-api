from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from teams.models import Team, Person
from teams.serializers import TeamListRetrieveSerializer, BasePersonSerializer

TEAM_URL = reverse("teams:team-list")


def get_team_detail_url(team_id: int) -> str:
    return reverse("teams:team-detail", args=[team_id])


def create_sample_team(**params) -> Team:
    defaults = {
        "name": "Test team",
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_sample_person(**params) -> Person:
    defaults = {"first_name": "Laura", "last_name": "Smith", "email": "laura@gmail.com"}
    defaults.update(params)

    return Person.objects.create(**defaults)


class TeamApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team = create_sample_team()

        member1 = create_sample_person()
        member2 = create_sample_person(first_name="John", email="john@example.com")

        self.team.members.add(member1, member2)

    def test_list_teams(self) -> None:
        response = self.client.get(TEAM_URL)
        teams = Team.objects.annotate(number_of_members=Count("members"))
        serializer = TeamListRetrieveSerializer(teams, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data[0]["number_of_members"], 2)

    def test_retrieve_team(self) -> None:
        response = self.client.get(get_team_detail_url(self.team.pk))
        team = Team.objects.filter(pk=self.team.pk).annotate(
            number_of_members=Count("members")
        )[0]
        serializer = TeamListRetrieveSerializer(team)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_team(self) -> None:
        payload = {"name": "New Team"}
        response = self.client.post(TEAM_URL, payload)
        team = Team.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(team.name, "New Team")

    def test_update_team(self) -> None:
        payload = {"name": "Updated Team Name"}
        response = self.client.put(get_team_detail_url(self.team.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, "Updated Team Name")

    def test_delete_team(self) -> None:
        response = self.client.delete(get_team_detail_url(self.team.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)

    def test_list_team_members(self) -> None:
        response = self.client.get(get_team_detail_url(self.team.pk) + "members/")
        serializer = BasePersonSerializer(self.team.members, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_add_team_members(self) -> None:
        person1 = create_sample_person(first_name="Jack", email="j@ex.com")
        person2 = create_sample_person(first_name="Nick", email="n@ex.com")
        payload = {"members_to_add": [person1.pk, person2.pk]}
        response = self.client.put(
            get_team_detail_url(self.team.pk) + "members/", payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.members.count(), 4)

    def test_get_specific_team_member(self) -> None:
        team_member = self.team.members.all()[0]
        response = self.client.get(
            get_team_detail_url(self.team.pk) + f"members/{team_member.pk}/"
        )
        serializer = BasePersonSerializer(team_member)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_remove_specific_team_member(self) -> None:
        team_member = self.team.members.all()[0]
        response = self.client.delete(
            get_team_detail_url(self.team.pk) + f"members/{team_member.pk}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.members.count(), 1)


# PersonApiTests will be similar to TeamApiTests
