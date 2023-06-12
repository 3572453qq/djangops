import json
from channels.generic.websocket import WebsocketConsumer
import ansible_runner
import re
from django.contrib.auth.decorators import login_required,permission_required
from easyops.models import *

COLOR_DICT = {
    '31': [(255, 0, 0), (128, 0, 0)],
    '32': [(0, 255, 0), (0, 128, 0)],
    '33': [(255, 255, 0), (128, 128, 0)],
    '34': [(0, 0, 255), (0, 0, 128)],
    '35': [(255, 0, 255), (128, 0, 128)],
    '36': [(0, 255, 255), (0, 128, 128)],
}

COLOR_REGEX = re.compile(r'\[[0-9];(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m')

BOLD_TEMPLATE = '<span style="color: rgb{}; font-weight: bolder">'
LIGHT_TEMPLATE = '<span style="color: rgb{}">'


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

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def send_feedback(self, event_data):
        print('here is the event',event_data['event'])

        #去掉stdout里面的不可见字符
        control_chars = ''.join(map(chr, list(range(0,32)) + list(range(127,160))))
        control_char_re = re.compile('[%s]' % re.escape(control_chars))
        send_str = control_char_re.sub('', event_data['stdout'])

        
        #将ansi里面的颜色控制符转换成html的颜色后发出
        send_str = send_str.strip()
        if len(send_str) > 1:
            self.send(text_data=json.dumps({
                # 'message': event_data['stdout'] 
                'message': ansi_to_html(send_str),
                'event':event_data['event']
            }))

        return True

    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        playbook_id =  int(message)
        atask=list(ansibletasks.objects.filter(id=playbook_id).values())[0]
        print("atask is: ",atask)
        self.send(text_data=json.dumps({
            'message': message
        }))
        self.send(text_data=json.dumps({
            'message': 'hello'
        }))
        
        self.send(text_data=json.dumps({
            'message': str(self.scope["user"])
        }))

        self.send(text_data=json.dumps({
            'message': atask['playbook']
        }))

        print(type(self.scope["user"]))
        
        #如果没有登录，则直接返回，不执行
        if  str(self.scope["user"])=='AnonymousUser':
            self.send(text_data=json.dumps({'message': "no longer in a session, pls log in !"}))
            return False

        #判断当前用户是否有权限执行这个ansibleplaybook
        
        all_perm=self.scope["user"].get_all_permissions()
        print(type(all_perm))
        print('this is all perm',all_perm)

        

        perm_needed=atask['ansiblepriv']
        aplaybook = atask['playbook']

        if perm_needed not in all_perm:
            self.send(text_data=json.dumps({
            'message': 'you are not authorized to run this playbook:'+aplaybook
            }))
            return False
        
        extravars=atask['extravars']
        if extravars is None:  #没有参数
            r = ansible_runner.run_async(private_data_dir='/etc/ansible', playbook=aplaybook+'.yml',event_handler=self.send_feedback)
        else: #有参数
            extravars = json.loads(extravars)
            print(extravars)
            r = ansible_runner.run_async(private_data_dir='/etc/ansible', playbook=aplaybook+'.yml',extravars=extravars,event_handler=self.send_feedback)

        for event in r[1].events:
            try:
                print(event['event_data']['task'])
            except KeyError:
                pass

        log_addition(self.scope["user"], pagepermission, 'submit ansible playbook:'+aplaybook)
          


# class playbookConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

    # def send_feedback(self, event_data):
    #     self.send(text_data=json.dumps({
    #         'message': event_data['stdout']
    #     }))

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         print('in receive')
#         self.send(text_data=json.dumps({
#             'message': 'hello'
#         }))
#         r = ansible_runner.run_async(private_data_dir='/etc/ansible', playbook='nomadntp.yml',event_handler=self.send_feedback)