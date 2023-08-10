# Generated by Django 4.2 on 2023-04-24 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0013_alter_messages_contain_message_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elections',
            name='status',
            field=models.CharField(choices=[('published', 'Published'), ('completed', 'Completed'), ('pending', 'Pending'), ('active', 'Active')], default='active', max_length=15),
        ),
        migrations.CreateModel(
            name='election_position',
            fields=[
                ('unique_id', models.AutoField(primary_key=True, serialize=False)),
                ('postion_name', models.CharField(max_length=200)),
                ('tag_line', models.TextField(default='')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('elections', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.elections')),
            ],
        ),
        migrations.CreateModel(
            name='election_parties',
            fields=[
                ('unique_id', models.AutoField(primary_key=True, serialize=False)),
                ('party_name', models.CharField(max_length=200)),
                ('party_image', models.ImageField(blank=True, null=True, upload_to='election_officers/')),
                ('tag_line', models.TextField(default='')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('elections', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.elections')),
            ],
        ),
    ]
