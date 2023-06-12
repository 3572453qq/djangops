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
from djangops.settings import CMDB_MODELS
from django.contrib.auth.models import Permission
from .remotefile import MyHost
from django.http import FileResponse  
import paramiko
from easyops.models import *

@login_required
@csrf_exempt
def dirlist(request,dirid):
    l_dirid=eval(dirid)
    user_all_permissions = request.user.get_all_permissions()
    print(request.POST.get('target'))
    print("*****",request.POST.get('dir'))
    sub_dir=request.POST.get('target')
    onetake=request.POST.get('take')
    print('#####',onetake)
    # data = request.POST.items()
    
    # print(data.__next__())
    # print(data.__next__())
    # print(data.__next__())
    data = request.POST.dict()
    print(data)
    # 根据传入的id以及用户权限获取dir
    record = list(uploaddir.objects.filter(
        id=l_dirid, uploadpriv__in=user_all_permissions).values())
    ls_host = record[0]['host']
    li_port = record[0]['port']
    ls_username = record[0]['username']
    ls_password = record[0]['password']
    ls_dir = record[0]['dir']
    myhost=MyHost(ls_host,li_port,ls_username,ls_password)

    if  sub_dir is not None:
        ls_dir=onetake+'/'+sub_dir
    print('here is ls_dir',ls_dir)
    
    filemanager_list=myhost.kendoui_one_dir(ls_dir,'*')
    

    # print(filemanager_list)
    return JsonResponse(filemanager_list,safe=False)
   