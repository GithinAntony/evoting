# Generated by Django 4.1.7 on 2023-04-26 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0017_alter_elections_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='election_candidates',
            name='party',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='election_candidates_party_conn', to='elections.election_parties'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='election_candidates',
            name='position',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='election_candidates_position_conn', to='elections.election_parties'),
            preserve_default=False,
        ),
    ]