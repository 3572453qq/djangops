# Generated by Django 3.2 on 2021-10-15 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0009_auto_20211015_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sqlstatement',
            name='sqlstr',
            field=models.CharField(blank=True, max_length=21000, verbose_name='sql字符串'),
        ),
    ]
