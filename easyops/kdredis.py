#coding=utf-8
from django.http import JsonResponse
from django.http import HttpResponse
import json
from querystring_parser import parser
from easyops.models import *
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission
import redis  
import yaml
import pickle
from django.shortcuts import render
from .remotefile import MyHost
from datetime import datetime
import random,string
import pandas as pd

@login_required
@csrf_exempt
def listing(request,montoring_id):

    print('in listing')
    
    l_monitoing_id=eval(montoring_id)
    user_all_permissions = request.user.get_all_permissions()
    
    
    # 根据传入的id以及用户权限获取远程文件
    record = list(prometheusconfig.objects.filter(
        id=l_monitoing_id, prometheuspriv__in=user_all_permissions).values())
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_configfile = record[0]['configfile']
    print(ls_host,ls_username,ls_configfile)
    myhost=MyHost(ls_host,li_port,ls_username,ls_password)
    ls_localfile = myhost.downloadfile(ls_configfile,'/tmp')
    if ls_localfile == 'nofile':
        context_dict = {'module': 'index'}
        context_dict['ls_remotefile']="'nofile'"
        context_dict['ls_columns']="'nothing'"
        context_dict['ls_data']="'nothing'"
    else:  
         # 打开prometheus配置文件并获取配置内容
        with open(ls_localfile, 'r') as stream:
            try:
                abc=yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        
        # 将配置存放到redis中
        redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False)
        redis_client = redis.Redis(connection_pool=redis_pool)
        redis_client.set('pmmonitoring'+str(montoring_id), pickle.dumps(abc))

        # 从prometheus的配置中读取出scrape_configs，并将其格式转换为kendo能获取的列模式
        tab_count = 0
        tabs = []
        for config_i,scrape_config in enumerate(abc['scrape_configs']):
            tab_count = config_i+1  # 多了一组配置
            atab = {}
            static_configs = scrape_config['static_configs']
            atab['tab_name']=scrape_config['job_name']
            
            # 先得到所有的列名
            first_line_labels = static_configs[0]['labels']
            ls_columns = list(first_line_labels.keys())
            print(ls_columns)
            ls_columns.insert(0,'id')
            atab['columns']=ls_columns

            # 然后得到data的内容
            ls_data = []
            for i,a_line in enumerate(static_configs):
                ls_data.append(a_line['labels'])
                ls_data[i]['id']=i+1
            atab['ls_data']=ls_data

            tabs.append(atab)

        context_dict = {'module': 'index'}
        context_dict['ls_columns']=ls_columns
        context_dict['ls_data']=ls_data
        context_dict['ls_remotefile']="'"+ls_configfile+"'"
        context_dict['ls_id']=montoring_id
        context_dict['tab_count']=tab_count
        context_dict['tabs']=tabs

    return render(request, 'easyops/prometheus_config.html', context_dict)

def uploadandrestart(l_monitoringid,abc_content,user_all_permissions,username):
     # 根据传入的id以及用户权限获取文件名称
    
    record = list(prometheusconfig.objects.filter(
        id=l_monitoringid, prometheuspriv__in=user_all_permissions).values())
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_configfile = record[0]['configfile']

    shortname = ls_configfile.split('/')[-1]
    ls_localfile = '/tmp/'+shortname+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+''.join(random.sample(string.ascii_letters, 3))
    with open(ls_localfile, 'w+') as stream:
        try:
            yaml.dump(abc_content, stream, allow_unicode=True,default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)
            print('ccccc')
            result_data = {"isok": 0, "errmsg": str(exc)}
    
    # 将文件拷贝到远端，并重启prometheus
    try:
        myhost=MyHost(ls_host,li_port,ls_username,ls_password)
        myhost.uploadfile(ls_localfile,ls_configfile)
        myhost.ssh.exec_command("systemctl restart prometheus")
        log_addition(username, pagepermission,
                            'restart prometheus:on ['+ls_host+']')  # 记录日志
        result_data = {"isok": 1}
    except Exception as e:
        print('aaaaaaa')
        result_data = {"isok": 0, "errmsg": str(e)}
    return result_data

@csrf_exempt
@login_required
def updateprometheus(request):

    # print(request.POST)
    prometheusid = request.POST.get('prometheusid')
    tabs = request.POST.get('tabs')
    tabs = json.loads(tabs)
    user_all_permissions = request.user.get_all_permissions()

    # 根据id从redis中获取配置文件内容
    redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False)
    redis_client = redis.Redis(connection_pool=redis_pool)
    
    abc=pickle.loads(redis_client.get('pmmonitoring'+str(prometheusid)))
    
    for tab_id,atab in enumerate(abc['scrape_configs']):

    # 从prometheus的配置中读取出scrape_configs
        static_configs = atab['static_configs']
        
        # 得到所有的列名
        first_line_labels = static_configs[0]['labels']
        ls_columns = list(first_line_labels.keys())
        # tabs = eval(tabs)
        ls_data=tabs[tab_id]['ls_data']
                
        # 将ls_data的值写到一个和static_configs相同的结构里面去
        new_static_configs = []
        for arow in ls_data:
            # print('*'*100)
            del arow['id'] 
            # print(arow)
            newrow={'labels':arow,'targets':[arow['ipaddress']]}
            new_static_configs.append(newrow)

        abc['scrape_configs'][tab_id]['static_configs']=new_static_configs
    
    result_data=uploadandrestart(prometheusid,abc,user_all_permissions,request.user)
    
    return JsonResponse(result_data)

def handle_uploaded_file(f,file_name):
    with open('/tmp/'+file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return '/tmp/'+file_name

@csrf_exempt
@login_required
def filetoprometheus(request,montoring_id):
    print(request.POST.get('tabname'))
    l_monitoing_id=eval(montoring_id)
    ls_tab_name=request.POST.get('tabname')
    user_all_permissions = request.user.get_all_permissions()
    print('this is tab_name in upload',ls_tab_name)
     # 根据id从redis中获取配置文件内容
    redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False)
    redis_client = redis.Redis(connection_pool=redis_pool)
    abc=pickle.loads(redis_client.get('pmmonitoring'+str(l_monitoing_id)))
    # print('this abc',abc)
    # 根据tabname找到对应的位置
    config_i = 10000
    for config_row,aconfig in enumerate(abc['scrape_configs']):
        if aconfig['job_name']==ls_tab_name:
            config_i=config_row


    file_static_configs=abc['scrape_configs'][config_i]['static_configs']
    labels_list = [config['labels'] for config in file_static_configs]
    df_files = pd.DataFrame(labels_list)
    # print('file_static_configs')
    # print(df_files)

    # 获取并解析传上来的文件：
    if request.method == 'POST':
        for filename, file in request.FILES.items():
            ls_filename=''.join(random.sample(string.ascii_letters, 3))+request.FILES[filename].name
            print('processing:',ls_filename)
            ls_filename=handle_uploaded_file(file,ls_filename)
            print('here:'+ls_filename)
    
    surfix=ls_filename.split('.')[-1].lower()
    print('here surfix',surfix)
    if surfix not in ['csv','xls','xlsx']:
        print('not vaild file')
        result_data = {"isok": 0, "errmsg": 'need excel file'}
        return JsonResponse(result_data)
    
    try:
        if surfix == 'csv':
            df_upload = pd.read_csv(ls_filename,encoding='gbk')
        else:
            df_upload = pd.read_excel(ls_filename)
        
        file_keys = df_files.columns.tolist()
        upload_keys = df_upload.columns.tolist()
        

        file_keys.append('id')
        print('file_keys',file_keys)
        print('upload_keys',upload_keys)
        file_keys.sort()
        upload_keys.sort()
        # print('comparison',file_keys==upload_keys)
        if file_keys != upload_keys:
            print('not matched')
            result_data = {"isok": 0, "errmsg": '错误的文件格式，正确的文件应该包含且只包含如下字段：'+' '.join(file_keys)}
            return JsonResponse(result_data)
        del df_upload['id']
    except Exception as e:
        print('bbbbb')
        result_data = {"isok": 0, "errmsg": str(e)}
        print(e)
        return JsonResponse(result_data)
    #合并
    df_all = pd.concat([df_files,df_upload])
    #去重
    df_all=df_all.drop_duplicates()
    
    # 将df转换成字典ls_data，且将ls_data的值写到一个和static_configs相同的结构里面去
    new_static_configs = []
    ls_data=df_all.to_dict('records')
    for arow in ls_data:
        newrow={'labels':arow,'targets':[arow['ipaddress']]}
        new_static_configs.append(newrow)
    
    abc['scrape_configs'][config_i]['static_configs']=new_static_configs

    # 根据传入的id以及用户权限获取文件名称
    result_data=uploadandrestart(l_monitoing_id,abc,user_all_permissions,request.user)
    print(result_data)
    return JsonResponse(result_data)
    # return HttpResponse(result_data)

if __name__ == "__main__":
    with open("/tmp/prometheus.yml", 'r') as stream:
        try:
            abc=yaml.safe_load(stream)
            print(abc)
            print('#'*100)
            print(abc['scrape_configs'][0]['static_configs'])
        except yaml.YAMLError as exc:
            print(exc)



    redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False)
    redis_client = redis.Redis(connection_pool=redis_pool)
    # redis_client.set('status', 'up')
    # print(redis_client.get('status'))
    # print(type(redis_client.get('status')))

    print(pickle.dumps(abc))

    redis_client.set('d', pickle.dumps(abc))
    defg=pickle.loads(redis_client.get('d'))
    print(defg)
    # print(type(redis_client.get('d')))