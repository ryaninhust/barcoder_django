#-*- coding: UTF-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from elaphe import barcode
from django.test import TestCase
from datetime import datetime
from Barcoder.service.models import *
from django.core import serializers
from django.http import *
from Barcoder.service import views
from django.utils.http import http_date,parse_http_date_safe
from calendar import timegm
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail



# def decomaker(arg):  
#     '通常对arg会有一定的要求'  
#     """由于有参数的 decorator函数在调用时只会使用应用时的参数  
#        而不接收被装饰的函数做为参数，所以必须在其内部再创建  
#        一个函数  
#     """  
#     def newDeco(func):    #定义一个新的decorator函数  
#         print func, arg  
#         return func  
#     return newDeco  
# @decomaker(deco_args)  
# def foo():pass      account=models.CharField(max_length=16)

# foo() 


def decomaker(arg):
    def newdeco(func):
        print func, arg
        return func
    return newdeco

@decomaker('asd')        
def a():
    print 'a'


if __name__ == "__main__":
    a=barcode('qrcode','Hello Barcode Writer In Pure PostScript.',options=dict(version=9, eclevel='M'), margin=10, data_mode='8bits')
    print a
    a.save('1.png')
#    for i in xrange(3):
#        send_mail('Subject here', 'Here is the message %d.'% i, '445405381@qq.com',
#    ['445405381@qq.com'], fail_silently=False,auth_user='445405381@qq.com',auth_password='yuanbowen1366714')
##    User_Activity.objects.get()
    
 
#    q=QueryDict('a=1&b=2&c=3')
#    print q.dict()
#    c=q.dict()
#    del c['a']
#    print c['a']
    
#    print Activity.objects.filter()
    
#    print datetime.datetime.now()>=o.timestamp
#    a=http_date(timegm(o.timestamp.utctimetuple()))
#    print datetime.datetime.strptime(a,'%a, %d %b %Y %H:%M:%S GMT')
#    print datetime.datetime.now()>datetime.datetime.strptime(a,'%a, %d %b %Y %H:%M:%S GMT')
#    print  type(a)
#    print http_date(timegm(o.timestamp.utctimetuple()))
#    print parse_http_date_safe(a)
    
#    u=User.objects.user_create(password="adsa",account="1233443347312",last_login=datetime.now())
#    a=Activity.objects.activity_create(name='asd',description='asd', date=datetime.now())
#    u_a= r_Activity.objects.create(user=u,activity=a,part_level=3,joined_time=datetime.now())
#    print serializers.serialize('json', [u_a])

#    request=HttpRequest()
#    request.method="POST"
#    request._raw_post_data=r'{"name": "\u539f\u535a\u6587", "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack", "timestamp": "2012-03-15 22:01:18", "exist_flag": true, "phone": "asd", "date": "2012-03-15 22:01:16", "email": "445405381@qq.com", "description": "\u6492\u5927\u53a6\u5927\u5927\u662f\u5927\u5927\u7684\u6492\u7684\u6492\u65e6\u6492\u65e6"}'
# 
#    print request.readline()
#       
#    views.Activty_list()(request)
    
    



#if __name__=='__main__':
#    a=Activity()
#    a.name='asd'
#    a.description='adsa'
#    a.date=datetime.now()
#    a.url='sadas'
#    a.email="asd"
#    a.phone='asd'
#    
#    a.save()
#    
#    o=Organization(name='asd1',last_login=datetime.now(),account='123456781112')
#    
#    o.save()
#    Activity_Organization.objects.create(activity=a,organization=o,level=1)
#    print a.host.filter(name='asd1').count()
#    
#    print serializers.serialize('json', Activity_Organization.objects.all())
#    try:
#        print Organization.objects.get(id=12)
#    except ObjectDoesNotExist:
#        print '123'
#        pass
#    

    
    
    
    


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
