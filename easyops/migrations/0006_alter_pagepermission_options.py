# Generated by Django 3.2 on 2021-10-15 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0005_dbconnection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagepermission',
            options={'permissions': (('killblocker', 'Can kill blocker'), ('viewebs', 'Can view ebs locker'), ('viewhr', 'Can view hr locker'), ('activesession', 'Can view activesession'), ('dbconnection', 'Can modify dbconnection'))},
        ),
    ]
