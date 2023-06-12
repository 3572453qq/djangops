import pandas as pd
import paramiko
import fnmatch
from datetime import datetime
import random,string
# your sftp config here

class MyHost:
    def __init__(self,host,port,username,password,max_dirs=100):
        self.host=host
        self.port=port
        self.username=username
        self.password=password
        self.max_dirs=max_dirs
        self.current_dirs=0

        paramiko.util.log_to_file("/tmp/paramiko.log")
        self.transport = paramiko.Transport((host,port))
        self.transport.connect(None,self.username,self.password)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, self.port, self.username, self.password, timeout=50)

    def kendoui_all_files(self,dir,wildcard):
        # print('#'*50,dir)
        file_list = []
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.chdir(dir)
        all_files=sftp.listdir()
        if len(all_files)==0: return []

        files = pd.DataFrame([attr.__dict__ for attr in sftp.listdir_attr()]) .sort_values("st_atime", ascending=False)
        # print(files)
        for i in range(len(files)):
            filemod = files.loc[i]['longname'].split(' ')[0]
            if filemod.startswith('d') or fnmatch.fnmatch(files.loc[i]['filename'],wildcard):
                last_dir=dir.split('/')[-1]
                # print(files.loc[i]['filename'],filemod)
                afile={}
                # print(files.loc[i]['filename'],filemod)
                afile['name']=files.loc[i]['filename']
                afile['size']=files.loc[i]['st_size']
                afile['size']=int(afile['size'])
                # afile['path']=dir+'/'+files.loc[i]['filename']
                afile['created']='/Date('+str(files.loc[i]['st_atime'])+'000)/'
                afile['createdUtc']="/Date("+str(files.loc[i]['st_atime'])+"000)/"
                afile['modified']='/Date('+str(files.loc[i]['st_mtime'])+'000)/'
                afile['modifiedUtc']="/Date("+str(files.loc[i]['st_mtime'])+"000)/"
                afile['extension']=""
                if filemod.startswith('d') and self.current_dirs < self.max_dirs and files.loc[i]['filename'][0]!='.': 
                    self.current_dirs += 1                   
                    afile['isDirectory']='true'    
                    afile['items']=self.kendoui_all_files(dir+'/'+files.loc[i]['filename'],wildcard)                
                    afile['path']=files.loc[i]['filename']
                else:
                    if filemod.startswith('d'):
                        afile['isDirectory']='true'
                        afile['items']=[]
                    else:
                        afile['isDirectory']='false'
                    afile['path']=last_dir
                afile['fullpath']=dir
                if files.loc[i]['filename'][0]!='.':
                    file_list.append(afile)
        return file_list

    def kendoui_one_dir(self,dir,wildcard):
        # print('#'*50,dir)
        file_list = []
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.chdir(dir)
        all_files=sftp.listdir()
        if len(all_files)==0: return []

        files = pd.DataFrame([attr.__dict__ for attr in sftp.listdir_attr()]) .sort_values("st_atime", ascending=False)
        # print(files)
        for i in range(len(files)):
            filemod = files.loc[i]['longname'].split(' ')[0]
            if filemod.startswith('d') or fnmatch.fnmatch(files.loc[i]['filename'],wildcard):
                last_dir=dir.split('/')[-1]
                # print(files.loc[i]['filename'],filemod)
                afile={}
                # print(files.loc[i]['filename'],filemod)
                afile['name']=files.loc[i]['filename']
                afile['size']=files.loc[i]['st_size']
                afile['size']=int(afile['size'])
                # afile['path']=dir+'/'+files.loc[i]['filename']
                afile['created']='/Date('+str(files.loc[i]['st_atime'])+'000)/'
                afile['createdUtc']="/Date("+str(files.loc[i]['st_atime'])+"000)/"
                afile['modified']='/Date('+str(files.loc[i]['st_mtime'])+'000)/'
                afile['modifiedUtc']="/Date("+str(files.loc[i]['st_mtime'])+"000)/"
                afile['extension']=""
                afile['isDirectory']='false'
                afile['path']=last_dir
                afile['fullpath']=dir
                if files.loc[i]['filename'][0]!='.':
                    file_list.append(afile)
        return file_list
    
    def uploadfile(self,localfile,remotefile):
        timeout=50
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        ls_cmd = 'test -e {0} && echo exists'.format(remotefile)
        print(ls_cmd)
        stdin, stdout, stderr = self.ssh.exec_command(ls_cmd)
        errs = stderr.read()
        if errs:
            raise Exception('Failed to check existence of {0}: {1}'.format(remotefile, errs))
        exists_str=str(stdout.read().decode())
        print('exist_str:',exists_str)
        file_exists = exists_str.strip() == 'exists'

        print('here file_exist',file_exists)
        if file_exists:
            ls_backupfile=remotefile+'.bak'+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+''.join(random.sample(string.ascii_letters, 3))
            ls_cmd = f'cp {remotefile} {ls_backupfile}'
            stdin, stdout, stderr = self.ssh.exec_command(ls_cmd)
            errs = stderr.read()
            if errs:
                raise Exception('Failed to backup files {0}: {1}'.format(remotefile, ls_backupfile))
        sftp.put(localfile,remotefile)

    def downloadfile(self,remotefile,local_dir):
        timeout=50
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        ls_cmd = 'test -e {0} && echo exists'.format(remotefile)
        print(ls_cmd)
        stdin, stdout, stderr = self.ssh.exec_command(ls_cmd)
        errs = stderr.read()
        if errs:
            raise Exception('Failed to check existence of {0}: {1}'.format(remotefile, errs))
        exists_str=str(stdout.read().decode())
        print('exist_str:',exists_str)
        file_exists = exists_str.strip() == 'exists'
        shortname = remotefile.split('/')[-1]
        if file_exists:
            ls_localfile = local_dir+'/'+shortname+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+''.join(random.sample(string.ascii_letters, 3))
            sftp.get(remotefile,ls_localfile)
            return ls_localfile
        else:
            return 'nofile'
        
       
        



if __name__ == "__main__":
    paramiko.util.log_to_file("paramiko.log")

    # Open a transport
    host,port = "172.16.3.101",22
    # Auth    
    username,password = "root","Genzon@#$nomad"
    dir='/tmp/test'
    wildcard='*.log'
    
    myhost=MyHost(host,port,username,password)
    # all_files=myhost.kendoui_all_files(dir,wildcard)
    myhost.ssh.exec_command('touch /tmp/touchme.txt')


    # ls_cmd = 'test -e {0} && echo exists'.format('/tmp/touchme.txt')
    ls_cmd = 'ls -ltr {0}'.format('/tmp/touchme111.txt')

    print(ls_cmd)
    stdin, stdout, stderr = myhost.ssh.exec_command(ls_cmd)
    print(str(stderr.read()))

    if not str(stderr.read()):                                                  
        is_directory_exists = True   

    
    errs = stderr.read()
    

    stdin, stdout, stderr = myhost.ssh.exec_command("test -e /tmp/2.cer && echo exists")
    # print(stdout.channel.recv_exit_status())    # status is 0
    print(stdout.read())
    stdin, stdout, stderr = myhost.ssh.exec_command("oauwhduawhd")
    print(stdout.channel.recv_exit_status())    # status is 127  

    file_exists = stdout.read().strip() == 'exists'
    # print('stdout',stdout.read().strip())
    # print('here file_exist',file_exists)
    # print(all_files)