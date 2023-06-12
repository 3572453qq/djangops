# Generated by Django 3.2 on 2021-12-09 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0021_auto_20211207_1433'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagepermission',
            options={'permissions': (('killblocker', 'Can kill blocker'), ('viewebs', 'Can view ebs locker'), ('viewhr', 'Can view hr locker'), ('activesession', 'Can view activesession'), ('dbconnection', 'Can modify dbconnection'), ('sqlconfig', 'Can modify sql statement'), ('sqlexec', 'Can exec sql statement'), ('appstartstop', 'Can start and stop app'), ('wikirestart', 'Can start and stop wiki'), ('nomadadmin', 'Can admin nomad servers'), ('ebsclone', 'Can clone ebs'), ('networkadmin', 'Can admin network'), ('ebsprod', 'Can admin ebsprod'), ('zijinprod', 'Can admin zijinprod'), ('ebstest', 'Can admin ebstest'), ('iamprod', 'Can admin iam'), ('oracledba', 'Can be oracledba'), ('mysqldba', 'Can be mysqldba'), ('sqlserverdba', 'Can be sqlserverdba'), ('cmdb', 'Can manage cmdb'), ('dba', 'Can act as dba'), ('admin', 'Can get into admin module'), ('ebsadmin', 'Can manage ebs prod'))},
        ),
    ]
