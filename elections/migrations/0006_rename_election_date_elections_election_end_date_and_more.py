# Generated by Django 4.1.7 on 2023-04-16 08:55
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0005_elections_election_officers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='elections',
            old_name='election_date',
            new_name='election_end_date',
        ),
        migrations.AddField(
            model_name='elections',
            name='election_start_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]