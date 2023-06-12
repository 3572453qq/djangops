# Generated by Django 3.2 on 2022-03-02 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0031_alter_pagepermission_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='wikidocs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('app_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='应用id')),
                ('docname', models.CharField(blank=True, max_length=128, null=True, verbose_name='文档名称')),
                ('extravars', models.CharField(blank=True, max_length=256, null=True, verbose_name='文档链接所带的参数')),
                ('wikipriv', models.CharField(blank=True, max_length=256, null=True, verbose_name='查看文档所需django权限')),
                ('wikilink', models.CharField(blank=True, max_length=1024, null=True, verbose_name='文档url')),
                ('desc', models.CharField(blank=True, max_length=256, null=True, verbose_name='文档描述')),
            ],
        ),
    ]
