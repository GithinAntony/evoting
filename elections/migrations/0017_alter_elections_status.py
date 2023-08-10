# Generated by Django 4.1.7 on 2023-04-26 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0016_alter_elections_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elections',
            name='status',
            field=models.CharField(choices=[('published', 'Published'), ('ready', 'Ready'), ('completed', 'Completed'), ('pending', 'Pending'), ('active', 'Active')], default='pending', max_length=15),
        ),
    ]