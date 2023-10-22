from django.contrib import admin

from teams.models import Team, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email"]


admin.site.register(Team)
