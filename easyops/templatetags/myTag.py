from django import template
import datetime
from django.conf import settings as conf_settings
from ..models import app
import json

register = template.Library()

 
@register.filter
def has_permisstion(user, perm):
 if user:
  return user.has_perm(perm)
 return False

@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)

@register.simple_tag
def expire_seconds():
    return conf_settings.SESSION_COOKIE_AGE

@register.simple_tag
def get_applist():
    fields=['id','appname']
    applist=app.objects.values(*fields)
    companypara=[]
    for aapp in applist:
        companypara.append({'value':aapp['id'],'text':aapp['appname']})
    companypara_json=json.dumps(companypara)
    return companypara_json


