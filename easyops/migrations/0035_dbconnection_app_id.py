# Generated by Django 3.2 on 2022-03-04 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0034_rename_db_wikidocs_app_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbconnection',
            name='app_id',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='应用id'),
        ),
    ]
