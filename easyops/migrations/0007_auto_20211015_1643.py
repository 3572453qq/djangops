# Generated by Django 3.2 on 2021-10-15 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0006_alter_pagepermission_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='sqlstatement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('dbname', models.CharField(blank=True, max_length=64, verbose_name='数据库名称')),
                ('sqlstr', models.CharField(blank=True, max_length=256, verbose_name='sql字符串')),
                ('sqldesc', models.CharField(blank=True, max_length=256, null=True, verbose_name='sql执行描述')),
            ],
        ),
        migrations.AlterModelOptions(
            name='pagepermission',
            options={'permissions': (('killblocker', 'Can kill blocker'), ('viewebs', 'Can view ebs locker'), ('viewhr', 'Can view hr locker'), ('activesession', 'Can view activesession'), ('dbconnection', 'Can modify dbconnection'), ('sqlconfig', 'Can modify sql statement'))},
        ),
        migrations.AlterField(
            model_name='dbconnection',
            name='dbdesc',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='数据库描述'),
        ),
    ]
