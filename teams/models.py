from django.db import models


class Team(models.Model):
    # Prevent creating teams with the same name
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    # A person can belong to several teams or not belong to any
    teams = models.ManyToManyField(Team, related_name="members", blank=True)

    class Meta:
        verbose_name_plural = "people"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
