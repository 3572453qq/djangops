from numpy import imag
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import socket
import re
from urllib import parse  

from selenium import webdriver
from PIL import Image
from django.conf import settings
import random,string,os,datetime

# 删除指定目录下超过指定天数的文件
def rmfiles(tododir='/tmp',expiredays=1):
    dirToBeEmptied = tododir #需要清空的文件夹
    ds = list(os.walk(dirToBeEmptied)) #获得所有文件夹的信息列表
    delta = datetime.timedelta(days=expiredays) #设定365天前的文件为过期
    now = datetime.datetime.now() #获取当前时间
    for d in ds: #遍历该列表
        os.chdir(d[0]) #进入本级路径，防止找不到文件而报错
        if d[2] != []: #如果该路径下有文件
            for x in d[2]: #遍历这些文件
                ctime = datetime.datetime.fromtimestamp(os.path.getmtime(x)) #获取文件修改时间
                if ctime < (now-delta): #若修改于delta天前
                    os.remove(x) #则删掉
# 端口检查
def port_check(ip_port_list):
    print(ip_port_list)
    check_result= {}
    check_result['summary']='ok'
    check_result['detail']=[]
    for ip_port in ip_port_list:
        ip = ip_port.split(':')[0].strip()
        port = int(ip_port.split(':')[1])
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            s.shutdown(2)
            print('%s:%d is used' % (ip, port))
            check_result['detail'].append(ip_port+' check ok')
        except socket.error as e:
            print('%s:%d is unused' % (ip, port))
            check_result['detail'].append(ip_port+' check error')
            check_result['summary']='error'
        check_result['imagefilename']=settings.STATIC_PATH+'/images/gz-logo.png'
    return check_result


# 登录检查web网站可用性，初始化传入url，用户名密码，是否iam，标志成功的文字，以及网页里定位username和password的文本输入框
class webcheck:
    def __init__(self,url,flagword,interval=1,browerser_type='chrome',islogin=False,isiam=False,iam_url='',username='',password='',txt_username='',txt_password='',txt_btn='',check_mode='django',av_check='web'):
        self.browerser_type=browerser_type
        self.url=url
        self.islogin=islogin
        self.isiam=isiam
        self.iam_url=iam_url
        self.username=username
        self.password=password
        self.flagword=flagword
        self.txt_username=txt_username
        self.txt_password=txt_password
        self.txt_btn=txt_btn
        self.interval=interval
        self.check_mode=check_mode
        self.av_check=av_check

        #为url添加上http
        if not self.url.startswith('http'):
            self.url='http://'+self.url
        #判断模拟什么浏览器，缺省使用chrome
        if self.browerser_type=='ie':
            pass
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--incognito")
            # options.add_experimental_option('prefs', {'intl.accept_languages': 'nl'})
            self.driver = webdriver.Chrome(options=options)
            # self.driver.delete_all_cookies()
            time.sleep(2)

# title = driver.title # 打印当前页面title
# now_url = driver.current_url # 打印当前页面URL
# # user = driver.find_element_by_class_name('nums').text # # 获取结果数目
# html = driver.page_source

    def getdriver(self):
        print('Getting driver of:',self.url)
        if self.islogin == True:
            if self.isiam == True:
                try:
                    self.driver.get(self.iam_url)
                except:
                    return False
            else:
                try:
                    self.driver.get(self.url)
                except:
                    return False
            # self.driver.find_element(By.ID,self.txt_username).send_keys(self.username)
            # self.driver.find_element(By.ID,self.txt_password).send_keys(self.password)

            # locate username input box and send username via id or placeholder
            time.sleep(self.interval)
            
            username_flag=False
            try:
                self.driver.find_element(By.ID,self.txt_username).send_keys(self.username)
                username_flag=True
            except:
                print('not be able to find username input by id:'+self.txt_username)
            
            if not username_flag:
                try:
                    location_str=self.txt_username
                    self.driver.find_element_by_xpath(location_str).send_keys(self.username)
                    username_flag=True
                except:
                    print('not be able to find username input by xpath:'+self.txt_username)

            # locate password input box and send password via id or placeholder
            password_flag=False
            try:
                self.driver.find_element(By.ID,self.txt_password).send_keys(self.password)
                password_flag=True
            except:
                print('not be able to find password input by id:'+self.txt_password)
            
            if not password_flag:
                try:
                    self.driver.find_element_by_xpath(self.txt_password).send_keys(self.password)
                    password_flag=True
                except:
                    print('not be able to find password input by xpath:'+self.txt_password)

            
            # locate submit button and send click event via id or class
            time.sleep(0.5)
            # print(self.driver.page_source)
            btn_flag=False
            try:
                self.driver.find_element(By.ID,self.txt_btn).click()
                btn_flag=True
            except:
                print('not be able to find by id:'+self.txt_btn)
            if not btn_flag:
                try:
                    self.driver.find_element_by_css_selector("[class='"+self.txt_btn+"']").click()
                    btn_flag=True
                except:
                    print('not be able to find button by class:'+self.txt_btn)
            if not btn_flag:
                try:
                    self.driver.find_element_by_xpath(self.txt_btn).click()
                    btn_flag=True
                except:
                    print('not be able to find button input by xpath:'+self.txt_btn)
            if not btn_flag:
                return False
            else:
                time.sleep(self.interval)
        else:
            try:
                self.driver.get(self.url)
            except:
                return False
        
        return True

    def gethtmlflag(self):
        check_result= {}
        check_result['summary']='ok'
        check_result['detail']=[]
        if self.isiam == True:
            try:
                self.driver.execute_script("window.open('"+self.url+"');")
            except Exception as e:
                print(str(e))
                check_result['detail'].append(self.url+' check error:'+str(e))
                check_result['summary']='error'
                return check_result

            time.sleep(self.interval)
            current_windows=self.driver.window_handles
            try:
                self.driver.switch_to.window(current_windows[-1])
            except:
                pass
        print('the url wanted is:',self.url)
        

        # print('the real url is:',self.driver.current_url)

        wanted_domain = parse.urlparse(self.url)   
        real_domain = parse.urlparse(self.driver.current_url) 

        
        print('wanted_domain is :',wanted_domain)
        print('real domain is',real_domain)
        if wanted_domain.netloc != real_domain.netloc and self.isiam == True:
            self.driver.find_element(By.ID,self.txt_username).send_keys(self.username)
            self.driver.find_element(By.ID,self.txt_password).send_keys(self.password)

            btn_flag=False
            try:
                self.driver.find_element(By.ID,self.txt_btn).click()
                btn_flag=True
            except:
                print('not be able to find by id:'+self.txt_btn)
            if not btn_flag:
                try:
                    self.driver.find_element_by_css_selector("[class='"+self.txt_btn+"']").click()
                    btn_flag=True
                except:
                    print('not be able to find by class:'+self.txt_btn)
            if not btn_flag:
                check_result['detail'].append(self.url+' check error:'+str(e))
                check_result['summary']='error'
                return check_result
            else:
                time.sleep(self.interval)

      
        tuple_time=time.localtime(time.time())
        strtime=time.strftime('%y-%m-%d-%H-%M-%S',tuple_time)
        
        #接下来存下本文件
        ls_filename = self.av_check.join(random.sample(string.ascii_letters, 3))+strtime+'.png'
        #当是django调用的时候，保存检查的截屏到django
        if self.check_mode=='django':
            rmfiles(settings.STATIC_PATH+'/images/tmp/',1) #先删除超过1天的截图文件
            self.driver.save_screenshot(settings.STATIC_PATH+'/images/tmp/'+ls_filename)
            im = Image.open(settings.STATIC_PATH+'/images/tmp/'+ls_filename)
            im.thumbnail((90,60))
            im.save(settings.STATIC_PATH+'/images/tmp/ss'+ls_filename,'PNG')
        else: #否则保存到/tmp/image目录下
            self.driver.save_screenshot('/tmp/image/'+ls_filename)
            rmfiles('/tmp/image/',3) #删除超过3天的截图文件

        check_result['imagefilename']=ls_filename

        #检查关键字是否存在于html里面
        htmlpage=self.driver.page_source
        # print(htmlpage)
        self.driver.quit()
        # print(htmlpage)
        if self.flagword in htmlpage:
            check_result['detail'].append(self.url+' check ok')
        else:
            print(htmlpage)
            check_result['detail'].append(self.url+' check error, key word ['+self.flagword+'] not found')
            check_result['summary']='error' 
        
        return check_result


if __name__ == "__main__":
    oaurl='http://oa.genzon.com.cn'
    iamurl='https://iam.genzon.com.cn/portal/login.html'
    username='huangchao'
    password='00Eljhbx!'

    # hrurl = 'https://dhr.genzon.com.cn/genzon/Home/HomeESS.aspx'
    # hrtest = webcheck(url=hrurl,flagword='人力资源系统',interval=1.5,browerser_type='chrome',
                        # islogin=True,isiam=True,iam_url=iamurl,
                        # username=username,password=password,txt_username='txt_username',
                        # txt_password='txt_password',txt_btn='btn')
    # if hrtest.getdriver():
    #     print(hrtest.gethtmlflag())

    # oatest = webcheck(url=oaurl,flagword='欢迎',interval=1.5,browerser_type='chrome',
    #                     islogin=True,isiam=True,iam_url=iamurl,
    #                     username=username,password=password,txt_username='txt_username',
    #                     txt_password='txt_password',txt_btn='btn')
    # if oatest.getdriver():
    #     print(oatest.gethtmlflag())

    


    # ebsurl='http://ebs.genzon.com.cn:8000/OA_HTML/AppsLocalLogin.jsp'
    # username='MAINTENANCE_DEP'
    # password='qwe123456'
    # ebstest=webcheck(url=ebsurl,flagword="menus['settingsMenu']",interval=1.5,browerser_type='chrome',
    #                     islogin=True,username=username,password=password,txt_username='usernameField',
    #                     txt_password='passwordField',txt_btn='OraButton left')

    # if ebstest.getdriver():
    #     print(ebstest.gethtmlflag())

    # xpath_username = '//*[@id="qzing-main"]/div/div[2]/div[4]/form/div[1]/div/div/input'
    xpath_username='//*[@placeholder="请输入帐号"]'
    xpath_password='//*[@placeholder="请输入密码"]'
    button_str = '//*[@class="el-button login-btn el-button--primary el-button--medium is-round"]'

    srmurl='https://srm.genzon.com.cn/mainframe/login'
    
    username='012539'
    password='123456'
    srmtest=webcheck(url=srmurl,flagword="SRM系统",interval=1.5,browerser_type='chrome',
            islogin=True,username=username,password=password,txt_username=xpath_username,
            txt_password=xpath_password,txt_btn=button_str,check_mode='standalone',av_check='SRM')

    if srmtest.getdriver():
        print(srmtest.gethtmlflag())