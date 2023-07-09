# coding=utf-8
from django.contrib import auth
from . import consumers
from django.contrib.auth import get_user_model
import ansible_runner
from django.db.models.expressions import Value
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import authenticate, login
import cx_Oracle as cx
import json
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from . import models
from .serializers import appSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from easyops.models import *
from django.forms.models import model_to_dict
import re
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.models import User, Permission
import pymysql
import pyodbc
from .MyEncoder import MyEncoder
import redis
from .remotefile import MyHost
from django.http import FileResponse  
import paramiko
# from models import pagepermission


def get_app_tree(app1, apptree):
    print(app1)
    apptree.append(app1)

    if app1['id'] > 1:
        appparent = list(app.objects.filter(
            id=app1['appparentid']).values())[0]
        # print('[',appparent)
        # apptree.append(appparent)
        get_app_tree(appparent, apptree)
    else:
        return


# Create your views here.

@login_required
def index(request):
    context_dict = {'module': 'index'}
    # print(request.user.username)
    # print(request.user.get_all_permissions())

    user_all_permissions = request.user.get_all_permissions()

    # 获取该用户有权限的app
    ansibleappids = list(ansibletasks.objects.filter(
        ansiblepriv__in=user_all_permissions).values('app_id').distinct())

    # 因为要作为参数传入app里面去做filter，因此需要将app_id转换为整型
    ansibleappids = [int(ansibleappid['app_id'])
                     for ansibleappid in ansibleappids]

    sqlappids = list(sqlstatement.objects.filter(
        sqlpriv__in=user_all_permissions).values('app_id').distinct())
    sqlappids = [int(sqlappid['app_id']) for sqlappid in sqlappids]

    grafanaappids = list(grafanareports.objects.filter(
        grafanapriv__in=user_all_permissions).values('app_id').distinct())
    grafanaappids = [int(grafanaappid['app_id'])
                     for grafanaappid in grafanaappids]

    wikiappids = list(wikidocs.objects.filter(
        wikipriv__in=user_all_permissions).values('app_id').distinct())
    wikiappids = [int(wikiappid['app_id']) for wikiappid in wikiappids]

    dbconnectionids = list(dbconnection.objects.filter(
        dbpriv__in=user_all_permissions).values('app_id').distinct())
    dbconnectionids = [int(dbconnectionid['app_id'])
                       for dbconnectionid in dbconnectionids]

    accheckids = list(availabilitycheck.objects.filter(
        acpriv__in=user_all_permissions).values('app_id').distinct())
    accheckids = [int(accheckid['app_id'])
                       for accheckid in accheckids]
    
    prometheusconfigids = list(prometheusconfig.objects.filter(
        prometheuspriv__in=user_all_permissions).values('app_id').distinct())
    prometheusconfigids = [int(prometheusconfigid['app_id'])
                       for prometheusconfigid in prometheusconfigids]
    
    appids = ansibleappids+sqlappids+grafanaappids+wikiappids+dbconnectionids+accheckids+prometheusconfigids
    # print(appids)
    applist = list(app.objects.filter(id__in=appids).values())
    # print(applist)

    apppara = []
    for aapp in applist:
        # 因为要跟playbook里面的app_id匹配，转成整型
        apppara.append({'value': str(aapp['id']), 'text': aapp['appname']})
    # apppara_json=json.dumps(apppara)
    context_dict['allapps'] = apppara

    # 创建侧边tree导航栏的applist
    apptree = []
    # onlyverylittlelist=applist=list(app.objects.filter(id__in=[1,25,26]).values())
    for app1 in applist:
        get_app_tree(app1, apptree)

    # print('apptree here:', apptree)
    apptree = list({v['id']: v for v in apptree}.values())
    newtree = []
    for dict_values in apptree:
        # result = {key:'' if value is None else value  for key,value in dict_values.items()} #将None取值变成空字符串
        # result['text']=result['appname']
        result = {}

        result['id'] = dict_values['id']
        result['parent'] = dict_values['appparentid']
        result['text'] = dict_values['appname']
        result['linksto'] = '#id'+str(dict_values['id'])
        newtree.append(result)

    apptree = newtree
    print('apptreeafter here:', apptree)
    # apptree=json.dumps(apptree)
    # print('apptreeafter json:',apptree)
    context_dict['apptree'] = apptree
    

    # 获取该用户有权限的playbook
    allplaybooks = list(ansibletasks.objects.filter(
        ansiblepriv__in=user_all_permissions).values())
    allplaybooks = sorted(allplaybooks, key=lambda k: k['desc'])

    newplayybooks = []
    allplaybookappids = []
    for dict_values in allplaybooks:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newplayybooks.append(result)
        allplaybookappids.append(result['app_id'])
    context_dict['allplaybooks'] = newplayybooks
    context_dict['allplaybookappids'] = allplaybookappids
    # print('here is playbookappids',context_dict['playbookappids'])

    # 获取该用户有权限的sql
    allsqls = list(sqlstatement.objects.filter(
        sqlpriv__in=user_all_permissions).values())
    allsqls = sorted(allsqls, key=lambda k: k['sqldesc'])

    newsqls = []
    allsqlappids = []
    for dict_values in allsqls:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        newsqls.append(result)
        allsqlappids.append(result['app_id'])
    context_dict['allsqls'] = newsqls
    context_dict['allsqlappids'] = allsqlappids

    # 获取该用户有权限的grafana
    allgrafanas = list(grafanareports.objects.filter(
        grafanapriv__in=user_all_permissions).values())
    allgrafanas = sorted(allgrafanas, key=lambda k: k['desc'])

    newgrafanas = []
    allgrafanaappids = []
    for dict_values in allgrafanas:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newgrafanas.append(result)
        allgrafanaappids.append(result['app_id'])
    context_dict['allgrafanas'] = newgrafanas
    context_dict['allgrafanaappids'] = allgrafanaappids

    # 获取该用户有权限的wiki
    allwikis = list(wikidocs.objects.filter(
        wikipriv__in=user_all_permissions).values())
    allwikis = sorted(allwikis, key=lambda k: k['desc'])
    newwikis = []
    allwikiappids = []
    for dict_values in allwikis:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newwikis.append(result)
        allwikiappids.append(result['app_id'])
    context_dict['allwikis'] = newwikis
    context_dict['allwikiappids'] = allwikiappids
    # print(context_dict['allwikiappids'])

    # 获取该用户有执行权限的db
    alldbs = list(dbconnection.objects.filter(
        dbpriv__in=user_all_permissions).values())
    alldbs = sorted(alldbs, key=lambda k: k['dbdesc'])
    # print('userallprivs:',user_all_permissions)
    # print('alldbs:',alldbs)
    newdbs = []
    alldbappids = []
    for dict_values in alldbs:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newdbs.append(result)
        alldbappids.append(result['app_id'])
    context_dict['alldbs'] = newdbs
    context_dict['alldbappids'] = alldbappids
    print('alldbappids', context_dict['alldbappids'])

    # 获取该用户有权限的avcheck
    allchecks = list(availabilitycheck.objects.filter(
        acpriv__in=user_all_permissions).values())
    allchecks = sorted(allchecks, key=lambda k: k['desc'])
    newchecks = []
    allacappids = []
    for dict_values in allchecks:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newchecks.append(result)
        allacappids.append(result['app_id'])
    context_dict['allchecks'] = newchecks
    context_dict['allacappids'] = allacappids
  

     # 获取该用户有权限的logfile
    logfiles = list(logfile.objects.filter(
        logpriv__in=user_all_permissions).values())
    logfiles = sorted(logfiles, key=lambda k: k['desc'])
    newfiles = []
    logfileids = []
    for dict_values in logfiles:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newfiles.append(result)
        logfileids.append(result['app_id'])
    context_dict['logfiles'] = newfiles
    context_dict['logfileids'] = logfileids

     # 获取该用户有权限的uploaddir
    uploaddirs = list(uploaddir.objects.filter(
        uploadpriv__in=user_all_permissions).values())
    uploaddirs = sorted(uploaddirs, key=lambda k: k['desc'])
    newdirs = []
    uploaddirids = []
    for dict_values in uploaddirs:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.itemsz() if value is not None}  #去掉取值是None的字段
        newdirs.append(result)
        uploaddirids.append(result['app_id'])
    context_dict['uploaddirs'] = newdirs
    context_dict['uploaddirids'] = uploaddirids

    # print(context_dict)
     # 获取该用户有权限的uploaddir
    prometheusconfigs = list(prometheusconfig.objects.filter(
        prometheuspriv__in=user_all_permissions).values())
    prometheusconfigs = sorted(prometheusconfigs, key=lambda k: k['desc'])
    newprometheusconfig = []
    prometheusconfigids = []
    for dict_values in prometheusconfigs:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.itemsz() if value is not None}  #去掉取值是None的字段
        newprometheusconfig.append(result)
        prometheusconfigids.append(result['app_id'])
    context_dict['prometheusconfig'] = newprometheusconfig
    context_dict['prometheusconfigids'] = prometheusconfigids

    return render(request, 'easyops/index.html', context_dict)


@login_required
@permission_required('easyops.cmdb')
def cmdb(request):
    # 获取permission里面的权限，并利用外键得到content_type里面的app_label(easyops,admin等等)
    from django.contrib.auth.models import Permission
    queryResult = Permission.objects.values_list(
        "codename", "content_type__app_label")
    # print('*'*30, queryResult)
    permissionwithlabel = [{'name': perm[1]+'.'+perm[0]}
                           for perm in queryResult]
    # print('#'*30, permissionwithlabel)

    context_dict = {'module': 'cmdb'}
    fields = ['id', 'appname']
    applist = app.objects.values(*fields)
    companypara = []
    for aapp in applist:
        companypara.append({'value': aapp['id'], 'text': aapp['appname']})
    companypara_json = json.dumps(companypara)
    context_dict['allapps'] = companypara_json
    context_dict['allprivs'] = permissionwithlabel
    # print(context_dict)
    return render(request, 'easyops/cmdb.html', context_dict)


@login_required
def f_adminsql(request, dbtype):
    context_dict = {'sub_module': 'adminsql', 'module': 'admin'}

    user_all_permissions = request.user.get_all_permissions()

    # 获取该用户有权限的sql
    allrecords = list(adminsql.objects.filter(
        sqlpriv__in=user_all_permissions, dbtype=dbtype).values())
    # allrecords=list(sqlstatement.objects.all().values())
    # allrecords=list(adminsql.objects.filter(dbtype=dbtype).values())

    # 解析每个sql里面是不是有绑定变量
    all_args = []
    for record in allrecords:
        if record['dbtype'] == 'oracle':
            ls_tempstr=re.sub('".*[:\.].*','',record['sqlstr'])
            ls_tempstr=re.sub("'.*[:\.].*'",'',ls_tempstr)
            args = re.findall(r':(\w+)', ls_tempstr)
        elif record['dbtype'] == 'mysql':
            args = re.findall(r'%\((\w+)\)', record['sqlstr'])
        else:
            args = []
        all_args.append(args)
        record['args'] = args

    # print('dbtype is:','['+dbtype+']','*'*30)
    context_dict['sqlstrs'] = allrecords
    context_dict['dbs'] = list(
        dbconnection.objects.filter(dbtype=dbtype).values())
    context_dict['args'] = all_args
    # print(context_dict)

    return render(request, 'easyops/adminsql.html', context_dict)


@login_required
@permission_required('easyops.dba')
def sql(request):
    context_dict = {'module': 'sql'}

    user_all_permissions = request.user.get_all_permissions()

    # 获取该用户有权限的sql
    allrecords = list(sqlstatement.objects.filter(
        sqlpriv__in=user_all_permissions).values())
    # allrecords=list(sqlstatement.objects.all().values())

    # 解析每个sql里面是不是有绑定变量
    all_args = []
    for record in allrecords:
        ls_dbname = record['dbname']
        ls_dbtype = dbconnection.objects.filter(
            dbname=ls_dbname).values('dbtype')[0]['dbtype']
        if ls_dbtype == 'oracle':
            ls_tempstr=re.sub('".*[:\.].*','',record['sqlstr'])
            ls_tempstr=re.sub("'.*[:\.].*'",'',ls_tempstr)
            args = re.findall(r':(\w+)', ls_tempstr)
        elif ls_dbtype == 'mysql':
            args = re.findall(r'%\((\w+)\)', record['sqlstr'])
        else:
            args = []
        all_args.append(args)
        record['args'] = args

    context_dict['sqlstrs'] = allrecords
    context_dict['args'] = all_args

    # print(context_dict)

    return render(request, 'easyops/sql.html', context_dict)


@login_required
def ansibleinstall(request):
    context_dict = {'module': 'ansibleinstall'}
    allrecords = list(Server.objects.all().values())
    context_dict['object_list'] = allrecords
    # print(context_dict)

    return render(request, 'easyops/ansibleinstall.html', context_dict)


@csrf_exempt
@login_required
def runsql(request):
    isok = 0
    # print(request.POST)
    l_runtype = eval(request.POST.get('runtype'))
    l_id = request.POST.get('sqlid')  # 当type为1和2时，是sqlid，当type是3时，是dbid
    # print('this is sqlid',l_id)
    if l_runtype == 1 or l_runtype == 2:
        arg = json.loads(request.POST.get('args'))  # 获得参数字典，通过json从字符串转换成字典类型
        argkeys = list(arg.keys())
    else:
        argkeys = []    # print('arg:',arg)

    if l_runtype == 1:    # 普通用户提交的sql，对应的数据库是固定的，包含在sql的定义中
        print(l_id)
        aline = sqlstatement.objects.filter(pk=l_id)
        ls_sqlstr = aline.values("sqlstr")[0]['sqlstr']
        ls_dbname = aline.values("dbname")[0]['dbname']
        # print(ls_dbname)
        ls_dbtype = dbconnection.objects.filter(
            dbname=ls_dbname).values('dbtype')[0]['dbtype']
        ls_connstr = dbconnection.objects.filter(
            dbname=ls_dbname).values('connstr')[0]['connstr']
        # print(ls_dbtype,ls_connstr)
        # print(ls_sqlstr)
    elif l_runtype == 2:  # dba用户提交的sql，对应的数据库是灵活的，包含在post信息中
        ls_dbtype = adminsql.objects.filter(
            pk=l_id).values('dbtype')[0]['dbtype']
        ls_dbname = request.POST.get('dbname')
        # print('this is dbtype',ls_dbtype)
        ls_connstr = dbconnection.objects.filter(
            dbname=ls_dbname).values('connstr')[0]['connstr']
        aline = adminsql.objects.filter(pk=l_id)
        ls_sqlstr = aline.values("sqlstr")[0]['sqlstr']
        print(ls_dbtype, ls_connstr)
    elif l_runtype == 3:  # 普通用户提交的sql，对应的数据库确定的dbid，需要执行的sql包含在post信息中
        ls_dbtype = dbconnection.objects.filter(
            pk=l_id).values('dbtype')[0]['dbtype']
        ls_dbname = dbconnection.objects.filter(
            pk=l_id).values('dbname')[0]['dbname']
        # print('this is dbtype',ls_dbtype)
        ls_connstr = dbconnection.objects.filter(
            dbname=ls_dbname).values('connstr')[0]['connstr']
        ls_sqlstr = request.POST.get('sqlstr')
        ls_sqlstr = ls_sqlstr.strip('"')  # 需要将引号去掉
        pattern = re.compile('[\t\n]+')
        ls_sqlstr = re.sub(r"\\n", ' ', ls_sqlstr)  # 将\n\t去掉
        print('sqlstr:', ls_sqlstr)
        print(ls_dbtype, ls_connstr)
    else:
        pass

    ls_sqlstr = ls_sqlstr.strip()
    # print(ls_sqlstr.upper())
    # print('ls_sql startwith',ls_sqlstr.upper().startswith('SELECT'))
    # print('raw str startwith','SELECT1 FROM DUAL'.startswith('SELECT'))
    if ls_sqlstr.upper().startswith('SELECT') == False:
        ls_data = {"isok": 0, "errmsg": 'not a select statement'}
        return HttpResponse(json.dumps(ls_data, cls=MyEncoder, indent=4))

    if ls_dbtype == 'oracle':
        try:
            con = cx.connect(ls_connstr)   # 创建连接
            cursor = con.cursor()   # 创建游标

            if len(argkeys) >= 1:  # 如果是带参数的sql
                cursor.execute(ls_sqlstr.strip(';'), arg)
            else:
                cursor.execute(ls_sqlstr.strip(';'))
            ls_desc = cursor.description
            # print(ls_desc)
            log_addition(request.user, pagepermission,
                         'sql execution:['+ls_sqlstr+'] on ['+ls_connstr+']')  # 记录日志
        except Exception as e:
            ls_data = {"isok": isok, "errmsg": str(e)}
            # return JsonResponse(ls_data)
            return HttpResponse(json.dumps(ls_data, cls=MyEncoder, indent=4))
    elif ls_dbtype == "mysql":
        try:
            db_host, db_user, db_pass, db_name = ls_connstr.split('|')
            con = pymysql.connect(host=db_host, user=db_user,
                                  password=db_pass, database=db_name)
            cursor = con.cursor(cursor=pymysql.cursors.Cursor)
            if len(argkeys) >= 1:  # 如果是带参数的sql
                cursor.execute(ls_sqlstr.strip(';'), arg)
            else:
                cursor.execute(ls_sqlstr.strip(';'))
            ls_desc = cursor.description
            log_addition(request.user, pagepermission,
                         'sql execution:['+ls_sqlstr+'] on ['+ls_connstr+']')  # 记录日志
        except Exception as e:
            ls_data = {"isok": isok, "errmsg": str(e)}
            return JsonResponse(ls_data)
    elif ls_dbtype == "sqlserver":
        try:
            con = pyodbc.connect(ls_connstr)
            cursor = con.cursor()   # 创建游标
            rows = cursor.execute(ls_sqlstr.strip(';'))
            ls_desc = cursor.description
            log_addition(request.user, pagepermission,
                         'sql execution:['+ls_sqlstr+'] on ['+ls_connstr+']')  # 记录日志
        except Exception as e:
            ls_data = {"isok": isok, "errmsg": str(e)}
            return JsonResponse(ls_data)
    else:
        isok = 0
        ls_data = {"isok": isok, "errmsg": 'not oracle or mysql or sqlserver'}
        return JsonResponse(ls_data)

    ls_columns = []

    print(ls_desc)

    for i, ls_column_tuple in enumerate(ls_desc):
        ls_column = ls_column_tuple[0]
        if len(ls_column) < 1:
            ls_column = str(i)

        ls_formated_column = re.sub('\W+', '_', ls_column)
        ls_formated_column = 'a' + \
            ls_formated_column if re.match(
                '^[0-9]', ls_formated_column) else ls_formated_column
        # print('column is',ls_formated_column)
        ls_columns.append(ls_formated_column)

    print('here are the columns', ls_columns)

    all_lines = []
    if ls_dbtype == 'oracle':
        for a_line in cursor:
            a_data = dict(zip(ls_columns, a_line))
            all_lines.append(a_data)
    elif ls_dbtype == 'mysql':
        for a_line in cursor.fetchall():
            a_data = dict(zip(ls_columns, a_line))
            all_lines.append(a_data)
    if ls_dbtype == 'sqlserver':
        for a_line in rows:
            # print(a_line)
            a_data = dict(zip(ls_columns, a_line))
            all_lines.append(a_data)
    else:
        pass

    # print(all_lines)

    cursor.close()
    con.close()

    isok = 1
    ls_data = {'data': all_lines, 'total': len(
        all_lines), 'columns': ls_columns, "isok": isok}
    # ls_pd_data = {'head': ls_columns, 'result':df.values.tolist()}
    # print(ls_data)

    print('****ls_data****:', json.dumps(ls_data, cls=MyEncoder, indent=4))
    # print('****ls_data****:',json.dumps(ls_data))
    if ls_dbtype == 'oracle':
        return HttpResponse(json.dumps(ls_data, cls=MyEncoder, indent=4))
    else:
        return JsonResponse(ls_data)
    #


@csrf_exempt
def appApi(request, aid=0):
    # print(aid)
    # print(request)
    if request.method == 'GET':
        apps = models.app.objects.all()
        apps_serializer = appSerializer(apps, many=True)
        print(apps_serializer.data)
        return JsonResponse(apps_serializer.data, safe=False)
    elif request.method == 'POST':
        app_data = JSONParser().parse(request)
        apps_serializer = appSerializer(data=app_data)
        if apps_serializer.is_valid():
            apps_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == 'PUT':
        app_data = JSONParser().parse(request)
        print(app_data)
        app = models.app.objects.get(app_id=app_data['app_id'])
        apps_serializer = appSerializer(app, data=app_data)
        if apps_serializer.is_valid():
            apps_serializer.save()
            return JsonResponse('Update successfully', safe=False)
        return JsonResponse('Failed to Update')
    elif request.method == 'DELETE':
        app = models.app.objects.get(app_id=aid)
        app.delete()
        return JsonResponse('Delete successfully', safe=False)


class InstallAppView(View):
    def post(self, request):
        app_list = json.loads(request.body).get("apps")
        host_list = json.loads(request.body).get("hosts")

        host_obj = Server.objects.filter(id__in=host_list).values("private_ip")
        ip_list = []
        for host in host_obj:
            ip_list.append(host.get("private_ip"))

        for app_id in app_list:
            if app_id == "0":
                Ansible_api(ip_list).run_playbook(
                    ["/etc/ansible/roles/jdk.yml"])
            elif app_id == "1":
                app_name = "nginx"
            elif app_id == "2":
                app_name = "zookeeper"

        return JsonResponse({'test': 'test'})


@login_required
def room(request, room_name):
    atask = list(ansibletasks.objects.filter(id=room_name).values())[0]
    app_id = atask['app_id']
    aapp = list(app.objects.filter(id=app_id).values())[0]
    app_name = aapp['appname']
    return render(request, 'easyops/room.html', {'room_name': room_name, 'playbook': atask['playbook'],
                                                 'desc': atask['desc'], 'app_name': app_name})


def runplaybook(request):
    print('in runplaybook')
    r = ansible_runner.run_async(private_data_dir='/etc/ansible', playbook='nomadntp.yml',
                                 event_handler=consumers.playbookConsumer.send_feedback)
    return JsonResponse(r.stats)


@login_required
def startstop(request):
    context_dict = {'module': 'startstop'}
    fields = ['id', 'appname']
    applist = app.objects.values(*fields)
    companypara = []
    for aapp in applist:
        companypara.append({'value': aapp['id'], 'text': aapp['appname']})
    companypara_json = json.dumps(companypara)
    context_dict['allapps'] = companypara_json
    print(context_dict)
    return render(request, 'easyops/startstop.html', context_dict)


@login_required
def standardop(request):
    print(request.user.username)
    # print(request.user.get_all_permissions())
    context_dict = {'module': 'admin'}
    user_all_permissions = request.user.get_all_permissions()

    # 获取该用户有权限的app
    appids = list(ansibletasks.objects.filter(
        ansiblepriv__in=user_all_permissions).values('app_id').distinct())

    # 因为要作为参数传入app里面去做filter，因此需要将app_id转换为整型
    appids = [int(appid['app_id']) for appid in appids]

    print(appids)
    applist = list(app.objects.filter(id__in=appids).values())
    # print(applist)

    apppara = []
    for aapp in applist:
        # 因为要跟playbook里面的app_id匹配，转成整型
        apppara.append({'value': str(aapp['id']), 'text': aapp['appname']})
    # apppara_json=json.dumps(apppara)
    context_dict['allapps'] = apppara

    # 获取该用户有权限的playbook
    allplaybooks = list(ansibletasks.objects.filter(
        ansiblepriv__in=user_all_permissions).values())

    newplayybooks = []
    for dict_values in allplaybooks:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        newplayybooks.append(result)
    context_dict['allplaybooks'] = newplayybooks

    # print(context_dict)
    return render(request, 'easyops/standardop.html', context_dict)


@login_required
def f_sqlstatement(request, sqlid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的sqlid以及用户权限获取sql
    record = list(sqlstatement.objects.filter(
        id=sqlid, sqlpriv__in=user_all_permissions).values())

    # 如果没有选择到数据
    if len(record) < 1:
        context_dict['sqlstr'] = {'sqlstr': 'You have no sql to execute'}
        context_dict['args'] = []
        context_dict['validsql'] = '0'
        return render(request, 'easyops/sqlstatement.html', context_dict)

    # print(record)
    # 解析每个sql里面是不是有绑定变量

    ls_dbname = record[0]['dbname']
    ls_dbtype = dbconnection.objects.filter(
        dbname=ls_dbname).values('dbtype')[0]['dbtype']
    if ls_dbtype == 'oracle':
        ls_tempstr=re.sub('".*[:\.].*','',record[0]['sqlstr'])
        ls_tempstr=re.sub("'.*[:\.].*'",'',ls_tempstr)
        args = re.findall(r':(\w+)', ls_tempstr)
    elif ls_dbtype == 'mysql':
        args = re.findall(r'%\((\w+)\)', record[0]['sqlstr'])
    else:
        args = []

    context_dict['sqlstr'] = record[0]
    context_dict['args'] = args
    context_dict['validsql'] = '1'
    return render(request, 'easyops/sqlstatement.html', context_dict)


@login_required
def dbroom(request, dbid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的dbid以及用户权限获取db
    record = list(dbconnection.objects.filter(
        id=dbid, dbpriv__in=user_all_permissions).values())

    # 如果没有选择到数据
    if len(record) < 1:
        context_dict['dbid'] = {
            'message': 'you have no right to this database'}
        return render(request, 'easyops/dbroom.html', context_dict)

    context_dict['dbid'] = dbid

    # print(context_dict)

    return render(request, 'easyops/dbroom.html', context_dict)


@csrf_exempt
@login_required
def addpermission(request):
    isok = 0
    # print(request.POST)
    privcode = request.POST.get('privcode')
    privname = request.POST.get('privname')

    content_type = ContentType.objects.get_for_model(pagepermission)
    try:
        permission = Permission.objects.create(
            codename=privcode,
            name=privname,
            content_type=content_type,
        )
        isok = 1
        ls_data = {"isok": isok}
    except Exception as e:
        ls_data = {"isok": isok, "errmsg": str(e)}
        # return JsonResponse(ls_data)
        return HttpResponse(json.dumps(ls_data, cls=MyEncoder, indent=4))
    return JsonResponse(ls_data)


@login_required
def listpermissions(request):
    context_dict = {'module': 'admin'}
    return render(request, 'easyops/listpermissions.html', context_dict)


@login_required
@csrf_exempt
def unlockjob(request):
    context_dict = {'module': 'admin'}
    killed = 'not requested'
    rds = redis.Redis(host='127.0.0.1', port=6379)
    if request.method == 'POST':        
        job_id = request.POST.get('job_id')
        print(job_id)
        lock_name = 'lock:job_'+str(job_id)
        try:
            rds.delete(lock_name)
            killed = 'yes'
        except:
            killed = 'no'
            pass

    context_dict['killed'] = killed

    locked_jobids=[]
    for key in rds.scan_iter("lock:job*"):
        lock_name = key.decode()
        jobid = int(lock_name.split('_')[1])
        locked_jobids.append(jobid)

    allplaybooks = list(ansibletasks.objects.filter(id__in=locked_jobids).values())
    # print('allplaybooks:',allplaybooks)
    newplayybooks = []
    allplaybookids = []
    for dict_values in allplaybooks:
        result = {key: '' if value is None else value for key,
                  value in dict_values.items()}  # 将None取值变成空字符串
        # result = {key:value  for key,value in dict_values.items() if value is not None}  #去掉取值是None的字段
        ls_appname = app.objects.filter(id=result['app_id']).values('appname')[0]['appname']
        result['id_appname_desc']=str(result['id'])+':'+ls_appname+result['desc']
        newplayybooks.append(result)
        allplaybookids.append(result['id'])
    newplayybooks = json.dumps(newplayybooks)
    allplaybookids = json.dumps(allplaybookids)

    # print('newplayybook',newplayybooks)
    context_dict['allplaybooks'] = newplayybooks
    context_dict['allplaybookids'] = allplaybookids

    return render(request, 'easyops/unlockjob.html', context_dict)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def sessionlock(ps_dbname):
    context_dict = {}

    sql_str = '''select decode(request, 0, 'Holder:', ' Waiter:') || s.inst_id || ':' ||
       s.sid || ',' || s.serial# sess,
       id1 || '/' || id2 "ID1ID2",
       l.type||':'||lmode || '/' || request "LMODEREQUEST",
       ctime,
       s.sql_id,
       s.event,
       s.last_call_et,
       s.status,
       s.username,
       s.machine,
       s.program
  from gv$lock l, gv$session s
 where (id1, id2, l.type) in
       (select id1, id2, type from gv$lock where request > 0)
   and l.sid = s.sid
   and l.inst_id = s.inst_id
 order by id1, ctime desc, request'''

    ls_connstr = dbconnection.objects.filter(
        dbname=ps_dbname).values('connstr')[0]['connstr']
    print('#'*30, ls_connstr)
    con = cx.connect(ls_connstr)
    cursor = con.cursor()   # 创建游标
    cursor.execute(sql_str)
    locked_session = dictfetchall(cursor)

    print(locked_session)

    for a_session in locked_session:
        ls_sql_id = a_session['SQL_ID']
        print(ls_sql_id)
        if ls_sql_id != None:
            sql_str = f"select SQL_TEXT from gv$sql where sql_id = '{ls_sql_id}' "
            print(sql_str)
            cursor.execute(sql_str)
            a_session['SQLTEXT'] = str(cursor.fetchall()[0])
        else:
            a_session['SQLTEXT'] = 'None'

    return json.dumps(locked_session)


@login_required
@csrf_exempt
@permission_required('easyops.admin')
def oracleunlock(request):
    context_dict = {}

    user_all_permissions = request.user.get_all_permissions()

    context_dict['dbs'] = list(
        dbconnection.objects.filter(dbpriv__in=user_all_permissions, dbtype='oracle', dbrole='system').values())
    context_dict['ispost'] = '0'

    if request.method == 'POST':
        ls_dbname = request.POST.get('dbname')
        print(ls_dbname, '*'*30)
        context_dict['locked_session'] = sessionlock(ls_dbname)
        context_dict['selecteddb'] = ls_dbname
        context_dict['ispost'] = '1'

    print(context_dict)
    return render(request, 'easyops/checklock.html', context_dict)


@login_required
@permission_required('easyops.admin')
def killblocker(request):
    print(request.path_info)
    killed = 0
    context_dict = {}
    ps_dbname = request.POST['dbname']
    print(ps_dbname, '#'*50)
    ls_connstr = dbconnection.objects.filter(
        dbname=ps_dbname).values('connstr')[0]['connstr']

    sql_str = '''select decode(request, 0, 'Holder:', ' Waiter:') || s.inst_id || ':' ||
       s.sid || ',' || s.serial# sess,
       id1 || '/' || id2 "ID1ID2",
       l.type||':'||lmode || '/' || request "LMODEREQUEST",
       ctime,
       s.sql_id,
       s.event,
       s.last_call_et,
       s.status,
       s.username,
       s.machine,
       s.program,
       s.sid,
       s.serial# s_number,
       s.inst_id
  from gv$lock l, gv$session s
 where (id1, id2, l.type) in
       (select id1, id2, type from gv$lock where request > 0)
   and l.sid = s.sid
   and l.inst_id = s.inst_id
   and s.status='INACTIVE'
 order by id1, ctime desc, request'''

    con = cx.connect(ls_connstr)
    cursor = con.cursor()   # 创建游标
    cursor.execute(sql_str)
    locked_session = dictfetchall(cursor)

    for a_session in locked_session:
        ls_sid = a_session['SID']
        ls_serial = a_session['S_NUMBER']
        ls_inst_id = a_session['INST_ID']
        sql_str = f"alter system kill session '{ls_sid},{ls_serial},@{ls_inst_id}'"
        cursor.execute(sql_str)
        killed = 1

    if killed == 1:
        log_addition(request.user, pagepermission,
                     'killed oracle session on:['+ls_connstr+']')
    return HttpResponse(killed)


@login_required
def check_job(request, jobid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的id以及用户权限获取avcheck
    record = list(availabilitycheck.objects.filter(
        id=jobid, acpriv__in=user_all_permissions).values())

    # 如果没有选择到数据
    if len(record) < 1:
        context_dict['checkjob'] = 'You have no right to performe this check :' + \
            str(jobid)
        context_dict['validcheck'] = '0'
        return render(request, 'easyops/checkjob.html', context_dict)
    context_dict['ac_id']=jobid

    #获取检查名称，检查类型，检查参数
    ls_acname = record[0]['acname']
    ls_appid = record[0]['app_id']
    ls_actype = record[0]['actype']
    ls_desc = record[0]['desc']
    aapp = list(app.objects.filter(id=ls_appid).values())[0]
    app_name = aapp['appname']
    if ls_actype == 'http':
        links = record[0]['vars']
        link_list = links.split(',')
        for link in link_list:
            print(link)

    context_dict['acname']=ls_acname
    context_dict['app_name']=app_name
    context_dict['desc']=ls_desc

    # context_dict['sqlstr'] = record[0]
    # context_dict['args'] = args
    # context_dict['validsql'] = '1'

    # print(context_dict)

    return render(request, 'easyops/avcheck.html', context_dict)


@login_required
def getlogfile(request, logfileid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的id以及用户权限获取logfile
    record = list(logfile.objects.filter(
        id=logfileid, logpriv__in=user_all_permissions).values())

    # 如果没有选择到数据
    if len(record) < 1:
        context_dict['logfile'] = 'You have no right to check this logfile :' + \
            str(logfileid)
        context_dict['validcheck'] = '0'
        return render(request, 'easyops/logfile.html', context_dict)
    context_dict['logfileid']=logfileid

    #获取检查名称，检查类型，检查参数
    ls_logfilename = record[0]['logfilename']
    ls_appid = record[0]['app_id']
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_dir = record[0]['dir']
    ls_wildcard = record[0]['wildcard']
    ls_desc = record[0]['desc']
    aapp = list(app.objects.filter(id=ls_appid).values())[0]
    app_name = aapp['appname']

    myhost=MyHost(ls_host,li_port,ls_username,ls_password)
    filemanager_list=myhost.kendoui_all_files(ls_dir,ls_wildcard)

    context_dict['logfilename']=ls_logfilename
    context_dict['app_name']=app_name
    context_dict['desc']=ls_desc
    context_dict['logfileid']=logfileid

    context_dict['filemanager_list']=filemanager_list

    return render(request, 'easyops/logfile.html', context_dict)

@csrf_exempt
@login_required
def file_download(request):
    isok = 0
    logfileid = eval(request.POST.get('logfileid'))
    name =  request.POST.get('name')
    fullpath =  request.POST.get('fullpath')

    user_all_permissions = request.user.get_all_permissions()
    # 根据传入的id以及用户权限获取logfile
    record = list(logfile.objects.filter(
        id=logfileid, logpriv__in=user_all_permissions).values())

    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_filename = fullpath+'/'+name
    try:
        local_dir='/tmp/'
        t = paramiko.Transport((ls_host,li_port))
        t.connect(username=ls_username,password=ls_password)
        sftp = paramiko.SFTPClient.from_transport(t)
    except Exception as E:
        print('ERROR connect to remote server', E)
        response=HttpResponse('error connect to remote server')
    else:
        sftp.get(ls_filename,local_dir+name)
        file = open(local_dir+name,'rb')
        response = FileResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename="'+name+'"'
        log_addition(request.user, pagepermission,
                         'downloadfile:['+ls_filename+'] on ['+ls_host+']')  # 记录日志
    
    return response

#为上传文件展示主机目录
@login_required
def getdir(request, uploaddirid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的id以及用户权限获取dir
    record = list(uploaddir.objects.filter(
        id=uploaddirid, uploadpriv__in=user_all_permissions).values())

    # 如果没有选择到数据
    if len(record) < 1:
        context_dict['dirname'] = 'You have no right to upload to the dir :' + \
            str(uploaddirid)
        context_dict['validcheck'] = '0'
        return render(request, 'easyops/uploaddir.html', context_dict)
    context_dict['uploaddirid']=uploaddirid

    #获取目录名称、appid、hostip等等
    ls_dirname = record[0]['dirname']
    ls_appid = record[0]['app_id']
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_dir = record[0]['dir']
    ls_desc = record[0]['desc']
    aapp = list(app.objects.filter(id=ls_appid).values())[0]
    app_name = aapp['appname']

    myhost=MyHost(ls_host,li_port,ls_username,ls_password)
    print(ls_host,li_port,ls_username,ls_password)
    filemanager_list=myhost.kendoui_all_files(ls_dir,'*')

    context_dict['dirname']=ls_dirname
    context_dict['app_name']=app_name
    context_dict['desc']=ls_desc
    context_dict['uploaddirid']=uploaddirid
    context_dict['dirpath']=ls_dir
    context_dict['host']=ls_host

    context_dict['filemanager_list']=filemanager_list

    return render(request, 'easyops/uploadfile.html', context_dict)

#接收上传文件
def handle_uploaded_file(f,file_name):
    with open('/tmp/'+file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@csrf_exempt
@login_required
def uploadfile(request,uploaddirid):
    context_dict = {'module': 'index'}
    user_all_permissions = request.user.get_all_permissions()

    # 根据传入的id以及用户权限获取dir
    record = list(uploaddir.objects.filter(
        id=uploaddirid, uploadpriv__in=user_all_permissions).values())
    
    if len(record) < 1:
        context_dict['dirname'] = 'You have no right to upload to the dir :' + \
            str(uploaddirid)
        context_dict['validcheck'] = '0'
        return render(request, 'easyops/uploaddir.html', context_dict)
    
    #获取目录名称、appid、hostip等等
    ls_dirname = record[0]['dirname']
    ls_appid = record[0]['app_id']
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_dir = record[0]['dir']
    ls_desc = record[0]['desc']
    aapp = list(app.objects.filter(id=ls_appid).values())[0]
    app_name = aapp['appname']
  
    myhost=MyHost(ls_host,li_port,ls_username,ls_password)
    if request.method == 'POST':
        for filename, file in request.FILES.items():
            ls_filename = request.FILES[filename].name
            print('processing:',ls_dir,ls_filename)
            handle_uploaded_file(file,ls_filename)
            print('here: /tmp/'+ls_filename)
            myhost.uploadfile('/tmp/'+ls_filename,ls_dir+'/'+ls_filename)
        
        return HttpResponse('true')

    # for filename, file in request.FILES.items():
    #     name = request.FILES[filename].name
    #     print(name)

    # print(request.FILES)