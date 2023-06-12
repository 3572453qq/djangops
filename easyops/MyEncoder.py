#为规避TypeError: Object of type 'type' is not JSON serializable问题，将json dumps在执行时遇到byte就变成str,但还是解决不了lob的问题
import json
from unicodedata import decimal
import cx_Oracle
import datetime
from decimal import Decimal
class MyEncoder(json.JSONEncoder):
    def default(self,obj):
        print('#'*30, 'in myencoder','#'*30)
        if  isinstance(obj,cx_Oracle.LOB):
            return ''
            # return str(obj,encoding='utf-8')
        elif isinstance(obj,bytes):
            # return str(obj,encoding='utf-8')
            return obj.decode("utf-8",'ignore')
        elif isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj,Decimal):
            return float(obj)
        elif isinstance(obj,float):
            return float(obj)
        elif isinstance(obj,int):
            return int(obj)
        else:
            return json.JSONEncoder.default(self,obj) 