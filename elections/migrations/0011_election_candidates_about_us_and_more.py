# Generated by Django 4.1.7 on 2023-04-17 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0010_alter_elections_election_end_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='election_candidates',
            name='about_us',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='election_candidates',
            name='manifestos',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='election_candidates',
            name='symbol',
            field=models.ImageField(blank=True, null=True, upload_to='candidates/'),
        ),
        migrations.AddField(
            model_name='election_candidates',
            name='tag_line',
            field=models.TextField(default=''),
        ),
    ]
