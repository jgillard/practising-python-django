# Generated by Django 2.1.7 on 2019-02-13 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_auto_20190208_0935'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonzoUser',
            fields=[
                ('id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('access_token', models.CharField(max_length=300)),
                ('refresh_token', models.CharField(max_length=300)),
                ('account_id', models.CharField(max_length=40)),
            ],
            options={
                'verbose_name_plural': 'MonzoUsers',
            },
        ),
    ]
