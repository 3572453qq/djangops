from availabilitycheck import *
import pymysql
import time
import json
import requests
import sys


def ac_check(ac_id):
    DATABASE_HOST = '172.16.4.201'
    DATABASE_USER = 'hc'
    DATABASE_PASSWORD = 'Abc_12345'
    DATABASE_NAME = 'djangops'

    #查询检查项
    db = pymysql.connect(host=DATABASE_HOST,user=DATABASE_USER,password=DATABASE_PASSWORD,database=DATABASE_NAME)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

    count = cursor.execute("select * from easyops_availabilitycheck where id="+str(ac_id))
    record=cursor.fetchall()
    
     #获取检查名称，检查类型，检查参数
    ls_acname = record[0]['acname']
    ls_appid = record[0]['app_id']
    ls_actype = record[0]['actype']
    ls_desc = record[0]['desc']
    ls_vars = record[0]['vars']
    print('*'*60,ls_vars)
    check_summary=[]
    if ls_actype=='collection':
        checks_list=ls_vars.split(',')
        print(checks_list)
        for acheck in checks_list:
            print('this acheck',acheck)
            print("select * from easyops_availabilitycheck where acname='"+acheck+"'")
            cursor.execute("select * from easyops_availabilitycheck where acname='"+acheck+"'")
            acheck_record= cursor.fetchall()
            as_acname = acheck_record[0]['acname']
            as_appid = acheck_record[0]['app_id']
            as_id = acheck_record[0]['id']
            as_actype = acheck_record[0]['actype']
            as_desc = acheck_record[0]['desc']
            as_vars = acheck_record[0]['vars']
            print('this is as_id',as_id)
            check_summary+=ac_check(as_id)
    elif ls_actype=='socket':
        ip_port_list=ls_vars.split(',')
        check_result=port_check(ip_port_list)
        check_summary = [{'check_name':ls_acname,'check_result':check_result}]
        print(check_result['detail'])        
    elif ls_actype == 'web':
        dic_vars = eval(ls_vars)
        print(dic_vars)
        checkjob = webcheck(url=dic_vars['url'],flagword=dic_vars['flagword'],interval=dic_vars['interval'],
                        browerser_type=dic_vars['browerser_type'],islogin=dic_vars['islogin'],
                        isiam=dic_vars['isiam'],iam_url=dic_vars['iamurl'],
                        username=dic_vars['username'],password=dic_vars['password'],
                        txt_username=dic_vars['txt_username'],txt_password=dic_vars['txt_password'],
                        txt_btn=dic_vars['txt_btn'],check_mode='standalone',av_check=ls_acname)
        if checkjob.getdriver():
            check_result=checkjob.gethtmlflag()
        else:
            check_result={}
            check_result['summary']='error'
            check_result['detail']=['not able to open the website:'+dic_vars['url']]
            check_result['imagefilename']='nofile'
        print(check_result['detail'])        
        check_summary = [{'check_name':ls_acname,'check_result':check_result}]
    else:
        pass

    return check_summary


if __name__ == "__main__":
    check_number = eval(sys.argv[1])
    dingding_token = sys.argv[2]
    print(check_number)
    print(dingding_token)

    check_all=ac_check(check_number)
    # print(check_all)
    # c_dingtalkUrl = 'https://oapi.dingtalk.com/robot/send?access_token=06443b072cea2690bdf558f36fec8ca5b455a8de547e7359237ff1391b13fb65'
    c_dingtalkUrl = 'https://oapi.dingtalk.com/robot/send?access_token='+dingding_token
    v_headers = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }

    for check_one in check_all:
        v_content={
            "msgtype": "markdown",
            "markdown": {
                            "title": "通知",
                            "text": "### 已完成检查：{} \
                            \n\n检查结果：{}，\
                            \n\n检查详细信息：{}".format(check_one['check_name'],
                                            check_one['check_result']['summary'], 
                                            check_one['check_result']['detail'][0])
                        }
        }
        print(v_content)
        if check_one['check_result']['summary'] != 'ok':
            r = requests.post(url=c_dingtalkUrl, headers=v_headers,
                                        data=json.dumps(v_content).encode("utf-8"))
            print(r.text)
            time.sleep(1)

