# Team API

Simple DRF-based api for teams and people.

## Features

- CRUD for teams
- CRUD for people
- Get list of team members
- Add list of people to the team
- Get a specific team member
- Delete a specific person from the team
- Get list of teams a person belongs to
- Add person to a list of teams
- Get a specific team a person belongs to
- Delete person from a specific team

## Installation

Python must be already installed

```shell
git clone git@github.com:TPolina/team-api.git
cd team-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirments.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata db_data.json
python manage.py runserver
```
You can use the following superuser:
Login: test.user
Password: Tbiol3ae8
