# Practising Python Django

## About

A continuation of the project started in https://github.com/jgillard/practising-go-tdd.

I intend to cover Django with a Postgres backend, Django Rest Framework, and maybe GraphQL.

## Installation

This has been developed with Python 3.7.3, and is currently using Django 2.2.0.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

A `settings_dev.ini` file is expected in the root of the project for local development.

In production this is substituted by environment variables in Heroku.

See the template `settings_dev.ini.template` for the required settings.

## Manual Steps
All setup has not been automated yet. This includes:

* Creation of 1 user in the `categories_monzouser` Postgres table
* Filling out `settings_dev.ini` for local development, or the Heroku env vars for the deployment.

## Tests

`./manage.py test`


## Deployment

Currently deployed on every push to master by Heroku.

Site available here: https://django-categories.herokuapp.com/