from . import views
from django.urls import include, path,re_path
from django.conf.urls import url
from easyops import views
from easyops import kdgriddml
from easyops import kdredis
from easyops import getdir
# from django.contrib.staticfiles.views import serve
# def return_static(request,path,insecure=True,**kwargs):
#     return serve(request,path,insecure,**kwargs)

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.index, name='root'),
    path('cmdb/', views.cmdb, name='cmdb'),
    path('sql/', views.sql, name='sql'),
    path('adminsql/', views.f_adminsql, name='adminsql'),
    url(r'^adminsql(?P<dbtype>[\w\-]+)$', views.f_adminsql, name='adminsql'),
    url(r'^app$', views.appApi),
    url(r'^app/([0-9]+)$', views.appApi),
    url(r'^listing/(?P<model_name>[\w\-]+)$',
        kdgriddml.listing, name='listing'),
    url(r'^updatelist/(?P<model_name>[\w\-]+)$',
        kdgriddml.updatelist, name='updatelist'),
    url(r'^create/(?P<model_name>[\w\-]+)$',
        kdgriddml.createnew, name='createnew'),
    url(r'^delete/(?P<model_name>[\w\-]+)$',
        kdgriddml.deleteone, name='deleteone'),
    url(r'^runsql$', views.runsql, name='runsql'),
    url(r'^ansibleinstall$', views.ansibleinstall, name='ansibleinstall'),
    path('ws<str:room_name>/', views.room, name='room'),
    url(r'^runplaybook$', views.runplaybook, name='runplaybook'),
    url(r'^startstop$', views.startstop, name='startstop'),
    url(r'^standardop', views.standardop, name='standardop'),
    url(r'^sqlstatement(?P<sqlid>\d+)$',
        views.f_sqlstatement, name='f_sqlstatement'),
    url(r'^database(?P<dbid>\d+)$', views.dbroom, name='dbroom'),
    url(r'^listpermissions$', views.listpermissions, name='listpermissions'),
    url(r'^addperm$', views.addpermission, name='addpermission'),
    url(r'^unlockjob$', views.unlockjob, name='unlockjob'),
    url(r'^oracleunlock$', views.oracleunlock, name='oracleunlock'),
    path('killblocker/', views.killblocker, name='killblocker'),
    url(r'^checkjob(?P<jobid>\d+)$', views.check_job, name='checkjob'),
    url(r'^getlogfile(?P<logfileid>\d+)$', views.getlogfile, name='getlogfile'),
    url(r'^file_download$', views.file_download, name='file_download'),
    url(r'^getdir(?P<uploaddirid>\d+)$', views.getdir, name='getdir'),
    url(r'^dirlist/(?P<dirid>\d+)$',
        getdir.dirlist, name='dirlist'),
    url(r'^uploadfile(?P<uploaddirid>\d+)$',views.uploadfile,name='uploadfile'),
    url(r'^pmmonitoring(?P<montoring_id>\d+)$',kdredis.listing,name='redislisting'),
    url(r'^updateprometheus$',kdredis.updateprometheus,name='updateprometheus'),
    url(r'^filetoprometheus(?P<montoring_id>\d+)$',kdredis.filetoprometheus,name='filetoprometheus'),
    # re_path(r'^static/(?P<path>.*)$',return_static,name='static'),  
]
 