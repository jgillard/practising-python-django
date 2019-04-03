# Generated by Django 2.1.7 on 2019-04-03 08:41

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0011_category_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashTransaction',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                                                         parent_link=True, primary_key=True, serialize=False, to='categories.Transaction')),
                ('amount', models.IntegerField(validators=[
                 django.core.validators.MaxValueValidator(-1)])),
                ('description', models.CharField(max_length=30)),
                ('merchant_name', models.CharField(max_length=30)),
                ('spend_date', models.DateField(default=datetime.datetime.now)),
                ('created', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'CashTransactions',
            },
            bases=('categories.transaction',),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.CharField(
                max_length=32, primary_key=True, serialize=False),
        ),
    ]
