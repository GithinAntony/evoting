# Generated by Django 4.2 on 2023-04-19 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0011_election_candidates_about_us_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_registration',
            name='otp_status',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=15),
        ),
    ]