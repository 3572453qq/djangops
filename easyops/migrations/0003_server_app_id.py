# Generated by Django 3.2 on 2021-10-12 02:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('easyops', '0002_ansibleexechistory_ansibleexectemplate_ansiblesyncfile_app_cloudak_disk_ecsauthssh_securitygroup_ser'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='app_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='server', to='easyops.app', verbose_name='业务系统ID'),
        ),
    ]
