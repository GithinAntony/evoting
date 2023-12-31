# Generated by Django 4.1.7 on 2023-04-29 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0025_election_votes_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election_votes',
            name='candidates',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates_conn', to='elections.election_candidates'),
        ),
    ]
