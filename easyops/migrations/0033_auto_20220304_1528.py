# Generated by Django 3.2 on 2022-03-04 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0032_wikidocs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagepermission',
            options={'permissions': (('killblocker', 'Can kill blocker'), ('viewebs', 'Can view ebs locker'), ('viewhr', 'Can view hr locker'), ('activesession', 'Can view activesession'), ('dbconnection', 'Can modify dbconnection'), ('sqlconfig', 'Can modify sql statement'), ('sqlexec', 'Can exec sql statement'), ('appstartstop', 'Can start and stop app'), ('wikirestart', 'Can start and stop wiki'), ('nomadadmin', 'Can admin nomad servers'), ('ebsclone', 'Can clone ebs'), ('networkadmin', 'Can admin network'), ('ebsprod', 'Can admin ebsprod'), ('zijinprod', 'Can admin zijinprod'), ('ebstest', 'Can admin ebstest'), ('iamprod', 'Can admin iam'), ('oracledba', 'Can be oracledba'), ('mysqldba', 'Can be mysqldba'), ('sqlserverdba', 'Can be sqlserverdba'), ('cmdb', 'Can manage cmdb'), ('dba', 'Can act as dba'), ('admin', 'Can get into admin module'), ('ebsadmin', 'Can manage ebs prod'), ('hqnetreport', 'Can view hq network charts'), ('oareport', 'Can view oa report'), ('ebsreport', 'Can view ebs report'), ('ztreport', 'Can view zhongtai report'), ('jdadmin', 'Can manage jiudian'), ('qhadmin', 'Can manage qiuhui'), ('lkadmin', 'Can manage lengku'), ('hrreport', 'Can view hr report'), ('ebssql', 'Can execute sql in ebs prod'))},
        ),
        migrations.RemoveField(
            model_name='wikidocs',
            name='app_id',
        ),
        migrations.AddField(
            model_name='dbconnection',
            name='dbpriv',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='在此数据库上执行sql所需权限'),
        ),
        migrations.AddField(
            model_name='wikidocs',
            name='db',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='应用id'),
        ),
    ]
