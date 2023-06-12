from django.db import models
from django.utils import timezone

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType


def log_addition(user, object, message):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr=user.username,
        action_flag=ADDITION,
        change_message=message
    )

# Create your models here.


class pagepermission(models.Model):
    class Meta:
        permissions = (("killblocker", "Can kill blocker"), ("viewebs", "Can view ebs locker"),
                       ("viewhr", "Can view hr locker"), ("activesession",
                                                          "Can view activesession"),
                       ('dbconnection', 'Can modify dbconnection'), ('sqlconfig',
                                                                     'Can modify sql statement'),
                       ('sqlexec', 'Can exec sql statement'), ('appstartstop',
                                                               'Can start and stop app'),
                       ('wikirestart', 'Can start and stop wiki'), ('nomadadmin',
                                                                    'Can admin nomad servers'),
                       ('ebsclone', 'Can clone ebs'), ('networkadmin',
                                                       'Can admin network'), ('ebsprod', 'Can admin ebsprod'),
                       ('zijinprod', 'Can admin zijinprod'), ('ebstest',
                                                              'Can admin ebstest'), ('iamprod', 'Can admin iam'),
                       ('oracledba', 'Can be oracledba'), ('mysqldba',
                                                           'Can be mysqldba'), ('sqlserverdba', 'Can be sqlserverdba'),
                       ('cmdb', 'Can manage cmdb'), ('dba',
                                                     'Can act as dba'), ('admin', 'Can get into admin module'),
                       ('ebsadmin', 'Can manage ebs prod'), ('hqnetreport',
                                                             'Can view hq network charts'), ('oareport', 'Can view oa report'),
                       ('ebsreport', 'Can view ebs report'), ('ztreport',
                                                              'Can view zhongtai report'), ('jdadmin', 'Can manage jiudian'),
                       ('qhadmin', 'Can manage qiuhui'), ('lkadmin',
                                                          'Can manage lengku'), ('hrreport', 'Can view hr report'),
                       ('ebssql', 'Can execute sql in ebs prod'), ('ebssqldg', 'Can execute sql in ebs proddg'))


CHARGE_TYPE_CHOOICE = (
    ('PrePaid', '包年包月'),
    ('PostPaid', '按量付费')
)


class app(models.Model):
    id = models.AutoField(primary_key=True)
    appname = models.CharField(
        max_length=64, verbose_name='业务系统名称', null=False, blank=True)
    apppriv = models.CharField(
        max_length=64, verbose_name='app管理权限', null=True, blank=True)
    appdesc = models.CharField(
        max_length=256, verbose_name='业务系统描述', null=True, blank=True)
    appparentid = models.IntegerField(
        verbose_name='父app节点', null=False, default=1)


class Server(models.Model):
    """
    服务器资产表
    """
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    instance_id = models.CharField(
        max_length=32, verbose_name='实例id', null=True, blank=True)
    hostname = models.CharField(
        max_length=64, verbose_name='主机名', null=False, blank=True)
    private_ip = models.GenericIPAddressField(
        verbose_name='私网IP', null=True, blank=True)
    public_ip = models.GenericIPAddressField(
        verbose_name='公网IP', null=True, blank=True)
    mac_address = models.CharField(
        max_length=32, verbose_name='物理地址', null=True, blank=True)
    bandwidth = models.IntegerField(
        verbose_name='带宽M', null=True, blank=True, default=0)
    cpu = models.IntegerField(verbose_name='CPU核数', null=True, blank=True)
    memory = models.IntegerField(verbose_name='内存/GB', null=True, blank=True)
    os_name = models.CharField(
        max_length=64, verbose_name='操作系统', null=True, blank=True)
    NETWORK_TYPE_CHOICES = (
        ('vpc', '专有网络'),
        ('classic', '经典网络')
    )
    network_type = models.CharField(max_length=16, choices=NETWORK_TYPE_CHOICES, verbose_name='网络类型', null=True,
                                    blank=True)
    expired_time = models.CharField(
        max_length=32, verbose_name='过期时间', null=True, blank=True)
    image_id = models.CharField(
        max_length=128, verbose_name='系统镜像', null=True, blank=True)
    INSTANCE_STATUS_CHOICES = (
        ('Running', '运行中'),
        ('Stopped', '已停止')
    )
    status = models.CharField(
        max_length=32, choices=INSTANCE_STATUS_CHOICES, verbose_name='实例状态', default='Running')
    security_group = models.CharField(
        max_length=1024, verbose_name='安全组', null=True, blank=True)
    vpc_id = models.CharField(
        max_length=128, verbose_name='VPC', null=True, blank=True)
    switch_id = models.CharField(
        max_length=128, verbose_name='交换机', null=True, blank=True)
    serial_numer = models.CharField(
        max_length=128, verbose_name='SN序列号', null=True, blank=True)
    os_type = models.CharField(
        max_length=16, verbose_name='操作系统类型', null=True, blank=True)
    create_time = models.CharField(
        max_length=32, verbose_name='创建时间', null=True, blank=True)
    zone_id = models.CharField(
        max_length=32, verbose_name='可用区', null=True, blank=True)
    region_id = models.CharField(
        max_length=32, verbose_name='所属地域', null=True, blank=True)

    instance_charge_type = models.CharField(max_length=32, choices=CHARGE_TYPE_CHOOICE, verbose_name='实例计费方式',
                                            null=True, blank=True)
    BANDWIDTH_TYPE_CHOICES = (
        ('PayByTraffic', '按流量计费'),
        ('PayByBandwidth', '按带宽计费')
    )
    internet_charge_type = models.CharField(max_length=64, choices=BANDWIDTH_TYPE_CHOICES, verbose_name='带宽计费方式',
                                            null=True, blank=True)
    # specs = models.CharField(max_length=254, verbose_name='实例规格', null=True, blank=True)
    # salecycle = models.CharField(max_length=32, verbose_name='实例计费周期', null=True, blank=True)
    comment = models.CharField(
        max_length=64, verbose_name='实例描述', null=True, blank=True)
    POWER_STATE_CHOICES = (
        ('poweredOn', '打开'),
        ('poweredOff', '关闭')
    )
    power_state = models.CharField(
        max_length=32, verbose_name='电源', choices=POWER_STATE_CHOICES, default='poweredOn')
    CLOUD_TYPE_CHOICES = (
        ('aliyun', '阿里云'),
        ('server', '物理机'),
        ('tencent', '腾讯云'),
        ('virtual_machine', '虚拟机'),

    )
    cloud_type = models.CharField(
        max_length=32, verbose_name='类型', choices=CLOUD_TYPE_CHOICES, default='aliyun')

    class Meta:
        db_table = 'server'
        ordering = ['instance_id']
        verbose_name = '服务器信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname

    @property
    def web_url(self):
        host = 'https://ecs.console.aliyun.com'
        url = f'{host}/#/server/{self.instance_id}/detail?regionId={self.region_id}'
        return url

    def to_dict(self):
        data = super().to_dict()
        print(data, 111)
        data['web_url'] = self.web_url
        return data


class CloudAK(models.Model):
    """
    阿里云ak
    """
    id = models.AutoField(primary_key=True)
    access_key = models.CharField(
        max_length=32, verbose_name='Access Key', null=True, blank=True, unique=True)
    access_secret = models.CharField(
        max_length=32, verbose_name='Access Secret', null=True, blank=True)
    active = models.BooleanField(verbose_name='启用状态', null=True, default=False)

    class Meta:
        db_table = 'cloud_ak'
        verbose_name = '阿里云AK'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.access_key


class Disk(models.Model):
    """
    磁盘
    """
    id = models.AutoField(primary_key=True)
    instance = models.ForeignKey('Server', verbose_name='实例ID', on_delete=models.SET_NULL, related_name='disk',
                                 null=True)
    disk_id = models.CharField(
        max_length=128, verbose_name='硬盘ID', null=True, blank=True)
    disk_name = models.CharField(
        max_length=64, verbose_name='硬盘名称', null=True, blank=True)
    CATEGORY_TYPE_CHOICES = (
        ('cloud', '普通云盘'),
        ('cloud_efficiency', '高效云盘'),
        ('cloud_ssd', 'SSD盘'),
        ('cloud_essd', 'ESSD云盘'),
    )
    category = models.CharField(
        max_length=32, verbose_name='硬盘类型', choices=CATEGORY_TYPE_CHOICES, default='cloud')
    device = models.CharField(
        max_length=128, verbose_name='设备名', null=True, blank=True)
    enable_auto_snapshot = models.BooleanField(
        verbose_name='自动快照策略', default=False)
    encrypted = models.BooleanField(verbose_name='是否加密', default=False)
    create_time = models.CharField(
        max_length=32, verbose_name='创建时间', null=True, blank=True)
    attached_time = models.CharField(
        max_length=32, verbose_name='挂载时间', null=True, blank=True)
    disk_charge_type = models.CharField(
        max_length=32, verbose_name='计费方式', choices=CHARGE_TYPE_CHOOICE)
    delete_with_instance = models.BooleanField(
        verbose_name='随实例释放', default=True)
    expired_time = models.CharField(
        max_length=32, verbose_name='过期时间', null=True, blank=True)
    description = models.CharField(
        max_length=128, verbose_name='硬盘描述', null=True, blank=True)
    size = models.IntegerField(verbose_name='硬盘大小/GiB', null=True, blank=True)
    DISK_STATUS_CHOICES = (
        ('In_use', '已挂载'),
        ('Available', '可用'),

    )
    status = models.CharField(
        max_length=32, verbose_name='状态', choices=DISK_STATUS_CHOICES)
    tags = models.CharField(
        max_length=128, verbose_name='标签', null=True, blank=True)
    serial_number = models.CharField(
        max_length=64, verbose_name='序列号', null=True, blank=True)
    DISK_TYPE_CHOICES = (
        ('system', '系统盘'),
        ('data', '数据盘')
    )
    type = models.CharField(
        max_length=32, verbose_name='盘类型', choices=DISK_TYPE_CHOICES)
    portable = models.BooleanField(verbose_name='是否可卸载', default=False)
    zone_id = models.CharField(
        max_length=32, verbose_name='所属可用区', null=True, blank=True)

    class Meta:
        db_table = 'disk'
        verbose_name = '硬盘管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.disk_id


class SecurityGroup(models.Model):
    """
    安全组
    """
    id = models.AutoField(primary_key=True)
    # instance_id = models.ManyToManyField('Server', verbose_name='服务器', null=True, blank=True)
    name = models.CharField(
        max_length=128, verbose_name='名称', null=True, blank=True)
    security_group = models.CharField(
        max_length=1024, verbose_name='安全组', null=True, blank=True)
    security_group_type = models.CharField(
        max_length=32, verbose_name='安全组类型', null=True, blank=True)
    desc = models.CharField(
        max_length=128, verbose_name='描述', null=True, blank=True)
    create_time = models.CharField(
        max_length=64, verbose_name='创建时间', null=True, blank=True)


class EcsAuthSSH(models.Model):
    """
    远程ssh 认证
    """
    id = models.AutoField(primary_key=True)
    AUTH_TYPE = (
        ('password', '密码认证'),
        ('key', '密钥认证')
    )
    type = models.CharField(
        max_length=32, verbose_name='认证方式', choices=AUTH_TYPE)
    username = models.CharField(verbose_name='用户名', max_length=64)
    password = models.CharField(
        verbose_name='密码', max_length=256, null=True, blank=True)
    key = models.TextField(verbose_name='密钥', null=True, blank=True)
    port = models.IntegerField(verbose_name='远程端口')
    SERVER_TYPE = (
        ('linux', 'linux'),
        ('windows', 'windows')
    )
    server_type = models.CharField(
        verbose_name='服务器类型', max_length=32, default='linux', choices=SERVER_TYPE)

    class Meta:
        db_table = 'ecs_ssh'
        verbose_name = 'SSH远程认证'
        verbose_name_plural = verbose_name


class AnsibleExecHistory(models.Model):
    """
    ansible 执行命令历史
    """

    COMMAND_TYPE = (
        ('shell', 'Shell命令'),
        ('win_shell', 'PowerShell命令'),
        ('playbook', 'Ansible PlayBook')
    )
    id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=128, verbose_name='任务名称')
    command_type = models.CharField(
        max_length=16, verbose_name='命令类型', choices=COMMAND_TYPE)
    execute_user = models.CharField(
        max_length=32, verbose_name='执行用户', default='root')
    created_at = models.CharField(max_length=128, verbose_name='创建时间')
    host_count = models.IntegerField(verbose_name='机器数量')
    command_content = models.TextField(max_length=1024, verbose_name='命令内容')
    job_id = models.CharField(max_length=128, verbose_name='任务id')
    job_status = models.CharField(
        max_length=12, verbose_name='任务状态', default='PENDING')
    command_id = models.CharField(max_length=128, verbose_name='命令id')

    class Meta:
        db_table = 'ansible_execute_history'
        verbose_name = 'Ansible执行记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.job_id


class AnsibleSyncFile(models.Model):
    """
    ansible 文件分发
    """
    id = models.AutoField(primary_key=True)
    execute_user = models.CharField(
        max_length=32, verbose_name='执行用户', default='root')
    created_at = models.CharField(max_length=128, verbose_name='创建时间')
    host_count = models.IntegerField(verbose_name='机器数量')
    job_id = models.CharField(max_length=128, verbose_name='任务id')
    job_status = models.CharField(
        max_length=12, verbose_name='任务状态', default='PENDING')
    command_id = models.CharField(max_length=128, verbose_name='命令id')
    dst_dir = models.CharField(max_length=512, verbose_name='目标路径')
    dst_filename = models.CharField(max_length=128, verbose_name='目标文件名称')
    src_filename = models.CharField(max_length=512, verbose_name='源文件名称')

    class Meta:
        db_table = 'ansible_sendfile_history'
        verbose_name = 'Ansible文件分发记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.job_id


class AnsibleExecTemplate(models.Model):
    """
    1、输入命令内容
    3、 shell    4、powershell
    2、选择已保存的命令模板
    5、ansible playbook
   """
    id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=128, verbose_name='模板名称')
    template_dsc = models.TextField(max_length=2048, verbose_name='描述')
    command_type = models.CharField(max_length=64, verbose_name='命令类型')
    template_dir = models.CharField(max_length=512, verbose_name='模板路径')
    created_at = models.CharField(max_length=128, verbose_name='创建时间')

    class Meta:
        db_table = 'ansible_execute_template'
        verbose_name = 'Ansible执行模板'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.template_name


class dbconnection(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    DB_TYPE_CHOICES = (
        ('mysql', 'mysql数据库'),
        ('oracle', 'oracle数据库'),
        ('sqlserver', 'sqlserver数据库')
    )
    dbtype = models.CharField(
        max_length=32, choices=DB_TYPE_CHOICES, verbose_name='数据库类型', null=False, blank=True)
    dbname = models.CharField(
        max_length=64, verbose_name='数据库名称', null=False, blank=True)
    connstr = models.CharField(
        max_length=256, verbose_name='连接字符串', null=False, blank=True)
    dbdesc = models.CharField(
        max_length=256, verbose_name='数据库描述', null=True, blank=True)
    dbpriv = models.CharField(
        max_length=256, verbose_name='在此数据库上执行sql所需权限', null=True, blank=True)
    dbrole = models.CharField(
        max_length=256, verbose_name='数据库角色', null=True, default='user', blank=True)


class sqlstatement(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    dbname = models.CharField(
        max_length=64, verbose_name='数据库名称', null=False, blank=True)
    sqlname = models.CharField(
        max_length=64, verbose_name='sql名称', null=False, blank=True)
    sqlstr = models.CharField(
        max_length=21000, verbose_name='sql字符串', null=False, blank=True)
    sqlpriv = models.CharField(
        max_length=256, verbose_name='sql执行所需django权限', null=True, blank=True)
    sqldesc = models.CharField(
        max_length=256, verbose_name='sql执行描述', null=True, blank=True)


class adminsql(models.Model):
    id = models.AutoField(primary_key=True)
    DB_TYPE_CHOICES = (
        ('mysql', 'mysql数据库'),
        ('oracle', 'oracle数据库'),
        ('sqlserver', 'sqlserver数据库')
    )
    dbtype = models.CharField(
        max_length=32, choices=DB_TYPE_CHOICES, verbose_name='数据库类型', null=False, blank=True)
    sqlname = models.CharField(
        max_length=64, verbose_name='sql名称', null=False, blank=True)
    sqlstr = models.CharField(
        max_length=21000, verbose_name='sql字符串', null=False, blank=True)
    sqlpriv = models.CharField(
        max_length=256, verbose_name='sql执行所需django权限', null=True, blank=True)
    sqldesc = models.CharField(
        max_length=256, verbose_name='sql执行描述', null=True, blank=True)


class ansibletasks(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    MODE_CHOICES = (
        ('playbook', 'playbook模式'),
        ('adhoc', 'adhoc模式')
    )
    mode = models.CharField(max_length=32, choices=MODE_CHOICES,
                            verbose_name='模式', null=False, default='playbook')
    playbook = models.CharField(
        max_length=128, verbose_name='playbook名称', null=True, blank=True)
    host_pattern = models.CharField(
        max_length=128, verbose_name='adhoc下主机组', null=True, blank=True)
    module = models.CharField(
        max_length=128, verbose_name='adhoc下执行的模块', null=True, blank=True)
    extravars = models.CharField(
        max_length=2560, verbose_name='playboo或者module所带的参数', null=True, blank=True)
    ansiblepriv = models.CharField(
        max_length=256, verbose_name='执行ansible脚本所需django权限', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='脚本描述', null=True, blank=True)


class grafanareports(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    reportname = models.CharField(
        max_length=128, verbose_name='report名称', null=True, blank=True)
    extravars = models.CharField(
        max_length=256, verbose_name='report所带的参数', null=True, blank=True)
    grafanapriv = models.CharField(
        max_length=256, verbose_name='查看报表所需django权限', null=True, blank=True)
    reportlink = models.CharField(
        max_length=1024, verbose_name='报表url', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='报表描述', null=True, blank=True)


class wikidocs(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    docname = models.CharField(
        max_length=128, verbose_name='文档名称', null=True, blank=True)
    extravars = models.CharField(
        max_length=256, verbose_name='文档链接所带的参数', null=True, blank=True)
    wikipriv = models.CharField(
        max_length=256, verbose_name='查看文档所需django权限', null=True, blank=True)
    wikilink = models.CharField(
        max_length=1024, verbose_name='文档url', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='文档描述', null=True, blank=True)


class availabilitycheck(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    acname = models.CharField(
        max_length=128, verbose_name='可用性检查名称', null=True, blank=True)
    # interval = models.FloatField(
    #     max_length=128, verbose_name='可用性检查名称', null=True, default=1)
    # AC_TYPE_CHOICES = (
    #     ('http', 'web类型'),
    #     ('socket', 'socket类型'),
    #     ('db', '数据库类型'),
    #     ('collection', '检查集合')
    # )
    actype = models.CharField(max_length=32,
                              verbose_name='可用性检查类型', null=False, default='socket')
    vars = models.CharField(
        max_length=2560, verbose_name='可用性检查所需要的json格式参数', null=True, blank=True)
    acpriv = models.CharField(
        max_length=256, verbose_name='可用性检查所需django权限', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='可用性检查描述', null=True, blank=True)

class logfile(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    logfilename = models.CharField(
        max_length=128, verbose_name='日志下载名称', null=True, blank=True)
    host = models.CharField(max_length=32,
                              verbose_name='主机ip', null=False, default='127.0.0.1')
    port = models.IntegerField(
        verbose_name='主机端口', null=False, default=22)
    username = models.CharField(
        max_length=256, verbose_name='用户名', null=True, blank=True)
    password = models.CharField(
        max_length=256, verbose_name='密码', null=True, blank=True)
    dir = models.CharField(
        max_length=256, verbose_name='日志路径', null=True, blank=True)
    wildcard = models.CharField(
        max_length=256, verbose_name='日志通配符', null=True, blank=True)
    logpriv = models.CharField(
        max_length=256, verbose_name='日志下载所需django权限', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='日志下载描述', null=True, blank=True)

class uploaddir(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    dirname = models.CharField(
        max_length=128, verbose_name='上传目录名称', null=True, blank=True)
    host = models.CharField(max_length=32,
                              verbose_name='主机ip', null=False, default='127.0.0.1')
    port = models.IntegerField(
        verbose_name='主机端口', null=False, default=22)
    username = models.CharField(
        max_length=256, verbose_name='用户名', null=True, blank=True)
    password = models.CharField(
        max_length=256, verbose_name='密码', null=True, blank=True)
    dir = models.CharField(
        max_length=256, verbose_name='上传目录全路径', null=True, blank=True)
    uploadpriv = models.CharField(
        max_length=256, verbose_name='上传文件所需django权限', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='上传文件描述', null=True, blank=True)

class prometheusconfig(models.Model):
    id = models.AutoField(primary_key=True)
    app_id = models.CharField(
        max_length=32, verbose_name='应用id', null=True, blank=True)
    prometheusname = models.CharField(
        max_length=128, verbose_name='prometheus监控名称', null=True, blank=True)
    host = models.CharField(max_length=32,
                              verbose_name='主机ip', null=False, default='127.0.0.1')
    port = models.IntegerField(
        verbose_name='主机端口', null=False, default=22)
    username = models.CharField(
        max_length=256, verbose_name='用户名', null=True, blank=True)
    password = models.CharField(
        max_length=256, verbose_name='密码', null=True, blank=True)
    configfile = models.CharField(
        max_length=256, verbose_name='带绝对路径文件名', null=True, blank=True)
    prometheuspriv = models.CharField(
        max_length=256, verbose_name='prometheus所需django权限', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='prometheus描述', null=True, blank=True)