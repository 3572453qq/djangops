import json

# from sqlalchemy import true
from channels.generic.websocket import WebsocketConsumer
import ansible_runner
import re
from django.contrib.auth.decorators import login_required, permission_required
from djangops.settings import WORKER_COUNT
from easyops.models import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
import string
import redis
import time
import uuid
from easyops.availabilitycheck import *

COLOR_DICT = {
    '31': [(255, 0, 0), (128, 0, 0)],
    '32': [(0, 255, 0), (0, 128, 0)],
    '33': [(255, 255, 0), (128, 128, 0)],
    '34': [(0, 0, 255), (0, 0, 128)],
    '35': [(255, 0, 255), (128, 0, 128)],
    '36': [(0, 255, 255), (0, 128, 128)],
}

COLOR_REGEX = re.compile(
    r'\[[0-9];(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m')

BOLD_TEMPLATE = '<span style="color: rgb{}; font-weight: bolder">'
LIGHT_TEMPLATE = '<span style="color: rgb{}">'

# 利用redis加锁


def acquire_lock(conn, lockname, acquire_timeout=10):
    print(lockname)
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.setnx('lock:' + lockname, identifier):
            return identifier
        time.sleep(.001)
    return False

# 利用redis解锁


def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname

    print('lockname', lockname)
    while True:
        try:
            pipe.watch(lockname)
            # print('locknameget:', str(pipe.get(lockname), encoding='utf-8'))
            print('identifier:', identifier)
            if str(pipe.get(lockname), encoding='utf-8') == identifier:
                pipe.multi()
                pipe.delete(lockname)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.exceptions.WatchError:
            print(lockname)
            pass
    return False


def ansi_to_html(text):
    text = text.replace('[0m', '</span>')

    def single_sub(match):
        argsdict = match.groupdict()
        if argsdict['arg_3'] is None:
            if argsdict['arg_2'] is None:
                color, bold = argsdict['arg_1'], 0
            else:
                color, bold = argsdict['arg_1'], int(argsdict['arg_2'])
        else:
            color, bold = argsdict['arg_2'], int(argsdict['arg_3'])

        if bold:
            return BOLD_TEMPLATE.format(COLOR_DICT[color][1])
        return LIGHT_TEMPLATE.format(COLOR_DICT[color][0])

    return COLOR_REGEX.sub(single_sub, text)


class runner_feedback:
    def __init__(self, room_group_name, c_name, job_name, job_lock):
        self.room_group_name = room_group_name
        self.c_name = c_name
        self.job_name = job_name
        self.job_lock = job_lock

    def send_feedback(self, event_data):
        print('here is the event', event_data['event'])
        channel_layer = get_channel_layer()

        send_str = event_data['stdout']
        send_str = send_str.replace('\n', '</br>')  # 将unix的换行改成html的换行

        # 去掉stdout里面的不可见字符
        control_chars = ''.join(
            map(chr, list(range(0, 32)) + list(range(127, 160))))
        control_char_re = re.compile('[%s]' % re.escape(control_chars))
        # send_str = control_char_re.sub('', event_data['stdout'])

        send_str = control_char_re.sub('', send_str)
        print(self.room_group_name)

        # 将ansi里面的颜色控制符转换成html的颜色后发出
        send_str = send_str.strip()
        # if len(send_str) > 1 and 'included:' not in send_str:
        if len(send_str) > 1 and event_data['event'] != 'playbook_on_include':
            # if len(send_str) > 1 :
            async_to_sync(channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "send.message",
                    'message': ansi_to_html(send_str),
                    'event': event_data['event']
                }
            )

            # self.send(text_data=json.dumps({
            #     # 'message': event_data['stdout']
            #     'message': ansi_to_html(send_str),
            #     'event':event_data['event']
            # }))

        if event_data['event'] == 'playbook_on_stats':
            rds = redis.Redis(host='127.0.0.1', port=6379)
            rds.set(self.c_name, 0)
            # rds.set(self.job_name,0)
            release_lock(rds, self.job_name, self.job_lock)

        return True
        



    
# 数据库连接性检查

# 可用性检查入口
def ac_check(ac_id, room_group_name):
    record = list(availabilitycheck.objects.filter(
        id=ac_id).values())
    
     #获取检查名称，检查类型，检查参数
    ls_acname = record[0]['acname']
    ls_appid = record[0]['app_id']
    ls_actype = record[0]['actype']
    ls_desc = record[0]['desc']
    ls_vars = record[0]['vars']
    print('*'*60,ls_vars)
    channel_layer = get_channel_layer()
    check_summary=[]
    if ls_actype=='collection':
        checks_list=ls_vars.split(',')
        for acheck in checks_list:
            acheck_record= list(availabilitycheck.objects.filter(
                        acname=acheck).values())
            as_acname = acheck_record[0]['acname']
            as_appid = acheck_record[0]['app_id']
            as_id = acheck_record[0]['id']
            as_actype = acheck_record[0]['actype']
            as_desc = acheck_record[0]['desc']
            as_vars = acheck_record[0]['vars']
            check_summary+=ac_check(as_id, room_group_name)
    elif ls_actype=='socket':
        ip_port_list=ls_vars.split(',')
        async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send.message",
                    "event": "check_single",
                    'message':ls_desc,
                }
            )
        check_result=port_check(ip_port_list)
        check_summary = [{'check_name':ls_acname,'check_result':check_result}]
        print(check_result['detail'])
        async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send.message",
                    "event": "check_socket",
                    'check_detail': check_result['detail'],
                    'check_result': check_result['summary'],
                    'imagefilename': check_result['imagefilename'],
                    'check_name': ls_acname,
                    "desc": ls_desc,
                    "message": 'check_socket message',
                }
            )
    elif ls_actype == 'web':
        dic_vars = eval(ls_vars)
        print(dic_vars)
        async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send.message",
                    "event": "check_single",
                    'message':ls_desc,
                }
            )

        checkjob = webcheck(url=dic_vars['url'],flagword=dic_vars['flagword'],interval=dic_vars['interval'],
                        browerser_type=dic_vars['browerser_type'],islogin=dic_vars['islogin'],
                        isiam=dic_vars['isiam'],iam_url=dic_vars['iamurl'],
                        username=dic_vars['username'],password=dic_vars['password'],
                        txt_username=dic_vars['txt_username'],txt_password=dic_vars['txt_password'],
                        txt_btn=dic_vars['txt_btn'],check_mode='django',av_check=ls_acname)
        if checkjob.getdriver():
            check_result=checkjob.gethtmlflag()
        else:
            check_result={}
            check_result['summary']='error'
            check_result['detail']=['not able to open the website:'+dic_vars['url']]
            check_result['imagefilename']='nofile'
        print(check_result['detail'])
        async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send.message",
                    "event": "check_url",
                    'check_detail': check_result['detail'],
                    'check_result': check_result['summary'],
                    'imagefilename': check_result['imagefilename'],
                    'check_name': ls_acname,
                    "desc": ls_desc,
                    "message": 'check_url message',
                }

            )
        check_summary = [{'check_name':ls_acname,'check_result':check_result}]
    else:
        pass
    # async_to_sync(channel_layer.group_send)(
    #             room_group_name,
    #             {
    #                 "type": "send.message",
    #                 "event": "check_end",
    #                 'message':'checkresult:'+str(check_result)
    #             }
    #         )
    
    async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send.message",
                    "event": "check_end",
                    'message':'check detail:'+check_summary[0]['check_name']
                }
            )
    # print()
    return check_summary
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('channel_name in connect', self.channel_name.split('.')[1])
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        astr = 'chat_%s_%s' % (self.room_name, ''.join(
            random.sample(string.ascii_letters, 8)))
        print('astr is', astr)
        self.room_group_name = 'chat_%s_%s' % (self.room_name, astr)
        self.c_name = 'noworker'
        self.job_name = 'job_'+self.room_name
        self.runned = False
        self.job_lock = False
        # self.room_group_name = "test"
        # Join room group
        self.accept()
        print('job_name is', self.job_name)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        rds = redis.Redis(host='127.0.0.1', port=6379)

        # 释放worker
        rds.set(self.c_name, 0)
        job_lock = rds.hget('all_jobs', self.job_name)

        # 只有当本次运行了任务的时候，退出的时候才将本次job的锁释放
        release_lock(rds, self.job_name, self.job_lock)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'ping':
            print(message)
            return True

        self.send(text_data=json.dumps({
            'message': 'hello'
        }))

        self.send(text_data=json.dumps({
            'message': str(self.scope["user"])
        }))

        self.send(text_data=json.dumps({
            'message': str(self.job_name)
        }))

        rds = redis.Redis(host='127.0.0.1', port=6379)
        print('room_name is:', self.room_name)

        # locked = acquire_lock(rds, self.job_name)
        # self.send(text_data=json.dumps({
        #         'message': str(locked)
        #     }))

        # 判断此任务是不是被其他人正在执行，如果是，则直接提示并退出
        if self.room_name.isdigit():  # 纯数字表示job number
            locked = acquire_lock(rds, self.job_name)
            self.send(text_data=json.dumps({
                'message': str(locked)
            }))
            print(locked)
            if not locked:
                self.send(text_data=json.dumps({
                    'message': "Someone is running this job right now,pls quit and run the job a while later"
                }))
                return False

            self.job_lock = locked
            self.runned = True

        # 判断是不是有worker可用
        self.c_name = 'noworker'
        for i in range(WORKER_COUNT):
            c_name_redis_key = 'c'+str(i)
            print(c_name_redis_key)
            if int(rds[c_name_redis_key]) == 0:
                rds.set(c_name_redis_key, 1)
                self.c_name = c_name_redis_key
                break

        if self.c_name == 'noworker':
            print('no worker avaliable')
            self.send(text_data=json.dumps({
                'message': '资源繁忙，请点击“退出”，三分钟后再进入本页面尝试'
            }))

            self.disconnect('close')

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # 如果没有登录，则直接返回，不执行
        if str(self.scope["user"]) == 'AnonymousUser':
            self.send(text_data=json.dumps(
                {'message': "no longer in a session, pls log in !"}))
            return False

        # 判断当前用户是否有权限执行这个ansibleplaybook
        playbook_id = int(message)
        atask = list(ansibletasks.objects.filter(id=playbook_id).values())[0]
        all_perm = self.scope["user"].get_all_permissions()
        print('this is all perm', all_perm)
        perm_needed = atask['ansiblepriv']
        print('this is playbook',atask['playbook'])
        self.send(text_data=json.dumps({
                'message': 'plabook:'+atask['playbook']
            }))
        print('this is extravars',atask['extravars'])
        self.send(text_data=json.dumps({
                'message': 'extravars:'+atask['extravars']
            }))
        amode = atask['mode']
        if amode == 'playbook':
            aplaybook = atask['playbook']+':'+atask['extravars']
        elif amode == 'adhoc':
            aplaybook = atask['host_pattern']+':' + \
                atask['module']+':'+atask['extravars']

        app_id = atask['app_id']
        appname = list(app.objects.filter(id=app_id).values())[0]['appname']

        if perm_needed not in all_perm:
            self.send(text_data=json.dumps({
                'message': 'you are not authorized to run this playbook:'+aplaybook
            }))
            return False

        async_to_sync(self.channel_layer.send)(
            self.c_name,
            {
                'type': 'chat.message',
                'message': message,
                'room_group_name': self.room_group_name,
                "c_name": self.c_name,
                "job_name": self.job_name,
                "job_lock": self.job_lock
            }
        )

        log_addition(self.scope["user"], pagepermission,
                     'submit ansible:'+aplaybook+' on app:['+appname+']')

    def send_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': event['event']
        }))

    def chat_message(self, event):
        print('channel_name in chat message', self.channel_name)
        message = event['message']
        # print(message)
        playbook_id = int(message)
        atask = list(ansibletasks.objects.filter(id=playbook_id).values())[0]
        # print("haha atask is: ",atask)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            event['room_group_name'],
            {
                "type": "send.message",
                'message': message,
                'event': 'common'
            }
        )

        async_to_sync(channel_layer.group_send)(
            event['room_group_name'],
            {
                "type": "send.message",
                'message': atask['playbook'],
                'event': 'common'
            }
        )

        mode = atask['mode']
        aplaybook = atask['playbook']
        host_pattern = atask['host_pattern']
        module = atask['module']
        extravars = atask['extravars']
        rf1 = runner_feedback(
            event['room_group_name'], event['c_name'], event['job_name'], event['job_lock'])

        if mode == 'playbook':
            if extravars is None or len(extravars) < 3:  # 没有参数
                r = ansible_runner.run_async(
                    private_data_dir='/etc/ansible', playbook=aplaybook+'.yml', event_handler=rf1.send_feedback)
                # r = ansible_runner.run(private_data_dir='/etc/ansible', playbook=aplaybook+'.yml',event_handler=rf1.send_feedback)
            else:  # 有参数
                extravars = json.loads(extravars)
                print(extravars)
                r = ansible_runner.run_async(
                    private_data_dir='/etc/ansible', playbook=aplaybook+'.yml', extravars=extravars, event_handler=rf1.send_feedback)
        elif mode == 'adhoc':
            r = ansible_runner.run(private_data_dir='/etc/ansible', host_pattern=host_pattern,
                                   module=module, module_args=extravars, event_handler=rf1.send_feedback)
            async_to_sync(channel_layer.group_send)(
                event['room_group_name'],
                {
                    "type": "send.message",
                    'message': 'adhoc命令执行完成，如果看不懂屏幕输出，您可能需要联系sa/dba确认最后执行结果。',
                    'event': 'common'
                }
            )
        else:
            async_to_sync(channel_layer.group_send)(
                event['room_group_name'],
                {
                    "type": "send.message",
                    'message': 'mode must be playbook or adhoc',
                    'event': 'common'
                }
            )

 
class AcConsumer(WebsocketConsumer):
    def connect(self):
        print('channel_name in connect', self.channel_name.split('.')[1])
        self.ac_id = self.scope['url_route']['kwargs']['ac_id']
        astr = 'acchat_%s_%s' % (self.ac_id, ''.join(
            random.sample(string.ascii_letters, 8)))
        print('astr is', astr)
        self.room_group_name = 'acchat_%s_%s' % (self.ac_id, astr)
        self.c_name = 'noworker'
        self.job_name = 'acjob_'+self.ac_id
        self.runned = False
        self.job_lock = False
        # self.room_group_name = "test"
        # Join room group
        self.accept()
        print('ac_name is', self.job_name)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        rds = redis.Redis(host='127.0.0.1', port=6379)

        # 释放worker
        rds.set(self.c_name, 0)


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'ping':
            print(message)
            return True

        self.send(text_data=json.dumps({
            'message': 'this is ac check hello'
        }))

        self.send(text_data=json.dumps({
            'message': str(self.scope["user"])
        }))

        self.send(text_data=json.dumps({
            'message': 'this is acid:'+str(self.ac_id)
        }))

        rds = redis.Redis(host='127.0.0.1', port=6379)
        print('ac_id is:', self.ac_id)

       
        # 判断是不是有worker可用
        self.c_name = 'noworker'
        for i in range(5, 5+WORKER_COUNT):
            c_name_redis_key = 'c'+str(i)
            print(c_name_redis_key)
            print(int(rds[c_name_redis_key]))
            if int(rds[c_name_redis_key]) == 0:
                rds.set(c_name_redis_key, 1)
                self.c_name = c_name_redis_key
                break
        # print("#"*30,self.c_name)
        if self.c_name == 'noworker':
            print('no worker avaliable')
            self.send(text_data=json.dumps({
                'message': '资源繁忙，请点击“退出”，三分钟后再进入本页面尝试'
            }))

            self.disconnect('close')

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.send(text_data=json.dumps({
            'message': 'room_group_name:'+str(self.room_group_name)
        }))
        # 如果没有登录，则直接返回，不执行
        if str(self.scope["user"]) == 'AnonymousUser':
            self.send(text_data=json.dumps(
                {'message': "no longer in a session, pls log in !"}))
            return False

        # 判断当前用户是否有权限执行这个ac检查
        ac_id = int(message)
        atask = list(availabilitycheck.objects.filter(id=ac_id).values())[0]
        all_perm = self.scope["user"].get_all_permissions()
        print('this is all perm in ac', all_perm)
        perm_needed = atask['acpriv']
        actype = atask['actype']

        app_id = atask['app_id']
        appname = list(app.objects.filter(id=app_id).values())[0]['appname']

        if perm_needed not in all_perm:
            self.send(text_data=json.dumps({
                'message': 'you are not authorized to run this check:'+appname
            }))
            return False

        async_to_sync(self.channel_layer.send)(
            self.c_name,
            {
                'type': 'ac.message',
                'message': message,
                'room_group_name': self.room_group_name,
                "c_name": self.c_name,
                "job_name": self.job_name,
                "job_lock": self.job_lock
            }
        )

        log_addition(self.scope["user"], pagepermission,
                     'submit check:'+self.job_name+' on app:['+appname+']')

    def send_message(self, event):
        message = event['message']
        if event['event'] == 'check_url' or event['event'] == 'check_socket':
            self.send(text_data=json.dumps({
                'message': message,
                'event': event['event'],
                'check_name': event['check_name'],
                'desc': event['desc'],
                'check_result': event['check_result'],
                'check_detail': event['check_detail'],
                'imagefilename': event['imagefilename'],
            }))
        else:
            self.send(text_data=json.dumps({
                'message': message,
                'event': event['event']
            }))

    def ac_message(self, event):
        print('channel_name in ac message', self.channel_name)
        message = event['message']
        # print(message)
        ac_id = int(message)
        atask = list(availabilitycheck.objects.filter(id=ac_id).values())[0]
        # print("haha atask is: ",atask)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            event['room_group_name'],
            {
                "type": "send.message",
                'message': message,
                'event': 'common'
            }
        )

        async_to_sync(channel_layer.group_send)(
            event['room_group_name'],
            {
                "type": "send.message",
                'message': atask['acname'],
                'event': 'common'
            }
        )

        actype = atask['actype']
        acname = atask['acname']

        # rf1 = runner_feedback(
        #     event['room_group_name'], event['c_name'], event['job_name'], event['job_lock'])
        async_to_sync(channel_layer.group_send)(
            event['room_group_name'],
            {
                "type": "send.message",
                'message': 'checking..., pls wait',
                'event': 'common'
            }
        )
        r = ac_check(ac_id,event['room_group_name'])
        for result in r:
            print(result)
            async_to_sync(channel_layer.group_send)(
                event['room_group_name'],
                {
                    "type": "send.message",
                    'message': result['check_name']+' returns: '+str(result['check_result']),
                    'event': 'check end'
                }
            )
        async_to_sync(channel_layer.group_send)(
                event['room_group_name'],
                {
                    "type": "send.message",
                    'message': 'check complete',
                    'event': 'check complete'
                }
            )
        rds = redis.Redis(host='127.0.0.1', port=6379)
        rds.set(event['c_name'], 0)

        # check_summary = [{'check_name':ls_acname,'check_result':check_result}]
        # r = ansible_runner.run(private_data_dir='/etc/ansible', playbook=aplaybook+'.yml',event_handler=rf1.send_feedback)
