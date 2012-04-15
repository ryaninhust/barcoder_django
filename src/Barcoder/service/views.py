#-*- coding: UTF-8 -*-

from Barcoder.service.barcoder_condition_get import condition, last_modified
from Barcoder.service.barcoder_http import HttpResponseError
from Barcoder.service.models import *
from datetime import datetime
from django.core import serializers
from django.http import *
from django.shortcuts import get_object_or_404
from django.utils import simplejson



#3-25的任务：
#1.加入max_result 2.加入start-index 3.加入querytag
#明日的任务队列
#1.完善错误码

status_code={'OK': 200,'CREATED':201,'ACCEPTED':202,'BAD REQUEST':400,'UNAUTHORIZED':401,\
             'FORBIDDEN':403,'NOT FOUND':404,'INTERNAL SERVER ERROR':500}
#def exist_flag_check():


#未完成的
def activtiy_list_condition_get(model):
    if model.if_modified_since is not None:
        return HttpResponse(serializers.serialize('json',Activity.objects.filter(timestamp__gt=model.if_modified_since,exist_flag=True) ),'application/json')
    else:
        return HttpResponse(serializers.serialize('json',Activity.objects.filter(exist_flag=True) ),'application/json') 
#def comment_list_condition_get(model):

#将url查询参数转换成字典格式
def querydict_to_dict(request):
    q=request.GET.dict()
    try:
        del q['start_index']
        del q['max_result']
    except Exception:
        #1.4最新功能函数（若用SAE需要注意）
        return request.GET.dict()
    else:
        return q

def get_partly_result(raw_result,request):
    querydic=request.GET
    start_index=querydic.get('start_index',0)
    max_result=querydic.get('max_result',10)
    if start_index>raw_result.count():
        #start_index超过了最大的游标
        return None
    if max_result>raw_result.count():
        return raw_result[start_index:]
    return raw_result[start_index:start_index+max_result]
    

   
#json转换成字典参数
def json_to_kwarg(json):
    return simplejson.loads(json)

#条件查询的控制参数（未完成）
def activity_last_mod_func():
    return Activity.objects.filter(exist_flag=True).latest('timestamp').timestamp


#json转换成实体
def update_from_json(model,json):
    data=simplejson.loads(json)
    for key,value in data.items():
        print key
        if key =='password':
            method=getattr(model, 'set_password')
            method(value)
            pass
        else:
            try:
           
                setattr(model, key, value)
                pass
            except AttributeError:
                raise AttributeError
           
    return model

#基础认证
def basic_auth(request):
    auth_info=request.META.get('HTTP_AUTHORIZATION',None)
    if auth_info and auth_info.startswith('Basic:'):
        result={}
        basic_info =auth_info.lstrip('Basic:')
        u,p=basic_info.decode('base64').split(':')
        result.setdefault('user',u)
        result.setdefault('password',p)
        return result
        pass
    else:
        return False

def check_user(result):
    if result is False:
        return False
    username=result.get('user',None)
    password=result.get('password',None)
    if username is  None or password is None:
        return False
    else:
        try:
            user=User.objects.get(account_email=username,exist_flag=True)
        except User.DoesNotExist:
            user=None    
        if user is not None:
            if  user.check_password(raw_password=password):
                return user
            else:
                return False
            pass
        else:
            return False
def login_required():
    def _protect(funcation):
        def __protect(*arg):
            result =basic_auth(arg[0].request)
            if check_user(result) is False:
                return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=1)
            #1为登录信息错误
            else:
                arg[0].auth_models=check_user(result)
                return funcation(*arg)
        return __protect
    return _protect
def permission_checked(urlmodel):
    def _protect(funcation):
        def __protect(*arg):
            if getattr(arg[0], urlmodel) not in getattr(arg[0].models, urlmodel+'_set').filter(exist_flag=True):
                response=HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
                #2为无权限管理相关内容
                return response
            else:
                return funcation(*arg)
        return __protect
    return _protect

def admin_checked(urlmodel):
    def _protect(funcation):
        def __protect(*arg):
            if arg[0].auth_models.is_host:
                org=arg[0].auth_models.organization
                arg[0].auth_model_organization=org
                if urlmodel is False:
                    return funcation(*arg)
                else:
                    if arg[0].activity  in org.activity_set.filter(level__gt=host_level_dic['cancel_level']):
                        return funcation(*arg)
                    else:
                        return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=3)
                    #3是没有权限访问该活动
                    pass
                pass
            else:
                return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=4)
                #4是该用户不是管理员
        return __protect
    return _protect
            

            
                    
                    
                
                    
    
            
   
#认证装饰
def authenticate(model,urlmodel,public,admin):
    def _protect(funcation):
        def __protect(*arg):
            #arg[0] is self !
            result=basic_auth(arg[0].request)
            if result:            
                try:
                    auth_models_objects=getattr(model, 'objects')
                    arg[0].auth_models=auth_models_objects.get(account=result.get('user'))
                    #password is not correct
                    if  not arg[0].auth_models.check_password(raw_password=result.get('password')):
                        return HttpResponseForbidden()
                    pass
                except model.DoesNotExist:
                    arg[0].auth_models=None
                    return HttpResponseForbidden()
                #my fault 
                except AttributeError:
                    return HttpResponseServerError()
                
                else:
                   
                        
                    if not public or urlmodel!=None:
                        if getattr(arg[0], urlmodel) not in getattr(arg[0].auth_models, urlmodel+'_set').all():
                            return HttpResponseForbidden()
                    return funcation(*arg)
                pass
            else:
                return HttpResponseForbidden()
            pass
        return __protect
    return _protect
 

#普通用户——活动——列表
class User_activity_list(object):
    def __call__(self,request,user_id):
        self.user=get_object_or_404(User,id =int(user_id))
        self.request=request
        try:
            callbackmethod=getattr(self, 'do_%s'% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    @login_required()
    def do_GET(self):
        if self.user!=self.auth_models:
            return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
        json=serializers.serialize(('json',), self.user.activity_set.filter(part_level_dic['participant_cancel']))
        return HttpResponse(json,mimetype='application/json')
    @login_required()
    def do_POST(self):
        if self.user!=self.auth_models:
            return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
        result_dict=json_to_kwarg(self.request.raw_post_data)
        
        activity_id=result_dict.get('activity',None)
        part_level=result_dict.get('part_level',None)
        if activity_id==None or part_level==None:
            return  HttpResponseError(status_code=status_code['BAD REQUEST'],error_code=5)
        #5缺少活动id或缺少参与程度
        activity=get_object_or_404(Activity,id=activity_id)
        u_a=User_Activity.objects.u_a_create(user=self.auth_models,activity=activity,part_level=part_level)
        return HttpResponse(serializers.serialize('json', [u_a]),mimetype="application/json")
    
 
class User_activity_detail(object):
    def __call__(self,request,user_id,activity_id):
        self.activity=get_object_or_404(Activity,id=int(activity_id))
        self.user=get_object_or_404(User,id=int(user_id))
        self.request=request
        try:
            callbackmethod=getattr(self,"do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    
    @login_required()
    @permission_checked('activity')
    def do_GET(self):
        if self.user!=self.auth_models:
            return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
        json=serializers.serialize('json', [get_object_or_404(User_Activity,user=self.auth_models,activity=self.activity)])
        response=HttpResponse(json,mimetype="application/json")
        return response
    @login_required()
    @permission_checked('activity')
    def do_PUT(self):
        if self.user!=self.auth_models:
            return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
        model=get_object_or_404(User_Activity,user=self.auth_models,activity=self.activity)
        try:
            pre_model=update_from_json(model, self.request.raw_post_data)
            pass
        except AttributeError:
            return HttpResponseBadRequest()
        else:
            pre_model.save()
            return HttpResponse(serializers.serialize('json', [pre_model]),mimetype="application/json")
    @login_required()
    @permission_checked('activity')
    def do_DELETE(self):
        if self.user!=self.auth_models:
            return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
        
        model=get_object_or_404(User_Activity,activity=self.activity,user=self.user)
        model.part_level=part_level_dic['participant_cancel']
        model.save()
        response=HttpResponse()
        response.status_code=status_code["OK"]
        return response
        
        
        


class User_list(object):
    ''' sign user'''
    def __call__(self,request):
#        print 'a'

        self.request=request
        
        try:
            callbackmethod=getattr(self,"do_%s" %request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()

        
    def do_POST(self):
        try:

            per_model=User.objects.user_create(**json_to_kwarg(self.request.raw_post_data))
            
            if per_model==None:
                return HttpResponseError(status_code=status_code['BAD REQUEST'],error_code=6)
            #6缺少足够的注册参数
            
        except Exception:
            
            return HttpResponseError(status_code=status_code['BAD REQUEST'],error_code=6)
        json=serializers.serialize('json', [User.objects.get(id=per_model.id)])
        return HttpResponse(json,mimetype='application/json')
    
        
            
        
        

    
class User_detail(object):
    """ user control"""
    def __call__(self,request,user_id):
        self.request=request
        self.user=get_object_or_404(User,id=int(user_id),exist_flag=True)
        try:
            callbackmethod=getattr(self, "do_%s"% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    def do_GET(self):
        self.user.password='secret'
        json=serializers.serialize('json', [self.user])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=200
        return response
    
    @login_required()
    def do_PUT(self):
        if self.auth_models !=self.user:
                return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
            
        else:
            try:
                update_model=update_from_json(self.user, self.request.raw_post_data)
                pass
            except AttributeError:
                return HttpResponseError(status_code=status_code['UNAUTHORIZED'],error_code=2)
            else:
                update_model.save()
                json=serializers.serialize('json', [User.objects.get(id=update_model.id)])
                response=HttpResponse(json,mimetype='application/json')
                response.status_code=200
                return response
            
            

    @login_required()
    def do_DELETE(self):
        if self.auth_models!=self.user:
            return HttpResponseForbidden()
        else:
            self.user.exist_flag=False
            self.user.save()
            response=HttpResponse()
            response.status_code=200
            return response
        
class Organization_activity_list(object):
        def __call__(self,request,organization_id):
            self.request=request
            self.organization=get_object_or_404(Organization,id=int(organization_id))
            try:
                callbackmethod=getattr('Organization_activity_list', 'do_%s'% request.method)
                pass
            except AttributeError:
                allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
                return HttpResponseNotAllowed(allowed_method)
            return callbackmethod()
        def do_GET(self):
            json=serializers.serialize('json', self.organization.activity_set.filter(exist_flag=True))
            response=HttpResponse(json,mimetype='application/json')
            response.status_code=status_code['ok']
            return response
        @login_required()
        @admin_checked(urlmodel=False)
        def do_POST(self):
            result_dict=json_to_kwarg(self.request.raw_post_data)
            activity=Activity.objects.activity_create(result_dict)
            act_org=Activity_Organization.objects.create(activity=activity,organization=self.auth_model_organization)
            json=serializers.serialize('json', [act_org])
            response=HttpResponse(json,mimetype='application/json')
            response.status_code=status_code['CREATED']
            
            
class Organization_activity_detail(object):
    def __call__(self,request,organization_id,activity_id):
        self.request=request
        self.organization=get_object_or_404(Organization,id=int(organization_id,exist_flag=1))            
        self.activity=get_object_or_404(Activity,id=int(activity_id,exist_flag=1))
        try:
            callbackmethod=getattr(self, "do_%s"% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    @login_required()
    @admin_checked(urlmodel=True)
    def do_GET(self):
        if self.organization!=self.auth_model_organization:
            return HttpResponseForbidden()
        o_a=get_object_or_404(Activity_Organization,activity=self.activity,organization=self.organization)
        return HttpResponse(serializers.serialize('json', [o_a]),mimetype="application/json")
    @login_required()
    @admin_checked(urlmodel=True) 
    def do_PUT(self):
        if self.organization!=self.auth_model_organization:
            return HttpResponseForbidden()
        o_a=get_object_or_404(Activity_Organization,activity=self.activity,organization=self.organization)
        try:
            pre_model=update_from_json(o_a, self.request.raw_post_data)
            pass
        except AttributeError:
            return HttpResponseBadRequest()
        pre_model.save()
        response=HttpResponse(serializers.serialize('json', [pre_model]),mimetype="application/json")
        response.status_code=status_code['ACCEPTED']
        return response
    @login_required()
    @admin_checked(urlmodel=True)
    def do_DELETE(self):
        if self.organization!=self.auth_model_organization:
            return HttpResponseForbidden()
        o_a=get_object_or_404(Activity_Organization,activity=self.activity,organization=self.organization)
        o_a.level=host_level_dic['cancel_level']
        o_a.save()
        response=HttpResponse()
        response.status_code=status_code['ACCEPTED']
        return response
 
class Organization_admin_list(object):
    def __call__(self,request,organization_id):
        self.request=request
        self.organization=get_object_or_404(Organization,id=organization_id,exist_flag=True)
        try:
            callbackmethod=getattr(self,'do_%s'% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    @login_required()
    @admin_checked(urlmodel=False)
    def do_GET(self):
        if self.auth_model_organization !=self.organization:
            response =HttpResponse()
            response.status_code=status_code['UNAUTHORIZED']
            return response
        json=serializers.serialize('json', [self.organization.admin])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response
class Organization_admin_detail(object):
    def __call__(self,request,organization_id,user_id):
        self.request=request
        self.organization=get_object_or_404(Organization,id=organization_id)
        self.user=get_object_or_404(User,id=user_id)
        try:
            callbackmethod=getattr(self,'do_%s'% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()  
    @login_required()
    @admin_checked(urlmodel=False)
    def do_PUT(self):
        self.organization.admin=self.user
        self.organization.save()
        json=serializers.serialize('json', [Organization.objects.get(id=self.organization.id)])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response      


            
class Activty_list(object):
    """获取活动信息表"""
    def __call__(self,request):
        self.request=request
        try:
            callbackmethod=getattr(self,'do_%s'% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
 
    @last_modified(activity_last_mod_func)
    def do_GET(self):
            if self.if_modified_since is not None:
                raw_result=Activity.objects.filter(timestamp__gt=self.if_modified_since,exist_flag=True,**querydict_to_dict(self.request))
                activity_list=get_partly_result(raw_result, self.request)

            else:
                raw_result=Activity.objects.filter(exist_flag=True,**querydict_to_dict(self.request))
                activity_list=get_partly_result(raw_result, self.request)
                return HttpResponse(serializers.serialize('json',Activity.objects.filter(**querydict_to_dict(self.request)) ),'application/json') 
            json=serializers.serialize('json', activity_list)
            response=HttpResponse(json,'application/json')
            response.status_code=status_code['OK']
            return response


    @login_required()
    @admin_checked(urlmodel=False)
    def do_POST(self):

        try:
            per_model= Activity.objects.activity_create(**json_to_kwarg(self.request.raw_post_data))
            if per_model==None:
                return HttpResponseBadRequest()
            pass
        except Exception:
            return HttpResponseBadRequest()
        
        Activity_Organization.objects.create(activity=per_model,organization=self.auth_model_organization,level=1)
        json=serializers.serialize('json', [Activity.objects.get(id=per_model.id)])
        return HttpResponse(json,mimetype='application/json')

        


class Activity_detail(object): 
    
    
    
    def __call__(self, request, activity_id):
        
        self.request = request
        self.activity=get_object_or_404(Activity,id=int(activity_id),exist_flag=1)
        
        try:
            callbackmethod = getattr(Activity_detail, "do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method = [m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self)
    

 
             
    def do_GET(self):
        
        json=serializers.serialize('json', [self.activity])
#        return HTTPBadRequest()
        response=HttpResponse(json, mimetype="application/json")
        response.status_code=status_code['OK']   
        return response
    @login_required()
    @admin_checked(urlmodel=True)
    def do_PUT(self):
        try:
            updated_model=update_from_json(self.activity, self.request.raw_post_data)
            pass
        except KeyError:
            return HttpResponseBadRequest()
        else:
            updated_model.save()
            json=serializers.serialize('json',[Activity.objects.get(id=updated_model.id)])
            response=HttpResponse(json,mimetype='application/json',status_code=200)
            response.status_code=status_code['ACCEPTED']
            return response
        
            
        
        

    @login_required()
    @admin_checked(urlmodel=True)
    def do_DELETE(self):
        self.activity.exist_flag=False
        self.activity.save()
        response=HttpResponse()
        response.status_code=status_code['ACCEPTED']
        return response
    
class Organization_detail(object):
    def __call__(self,request,org_id):
        self.request=request
        self.organization=get_object_or_404(Organization,id=org_id,exist_flag=1)
        try:
            callbackmethod=getattr(self, 'do_%s'% request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod()
    def do_GET(self):
        self.organization.password='secret'
        json=serializers.serialize('json', [self.organization])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=200
        return response
    @login_required()
    @admin_checked(urlmodel=False)
    def do_PUT(self):
        if self.auth_model_organization!=self.organization:
            return HttpResponseBadRequest()
        pre_model=update_from_json(self.organization, self.request.raw_post_data)
        pre_model.save()
        response=HttpResponse(serializers.serialize('json', [Organization.objects.get(id=pre_model.id)]),mimetype="application/json")
        response.status_code=202
        return response
        return
    @login_required()
    @admin_checked(urlmodel=False)
    def do_DELETE(self):
        if self.auth_model_organization!=self.organization:
            return HttpResponseBadRequest()
        self.organization.exist_flag=False
        self.organization.save()
        response=HttpResponse()
        response.status_code=status_code['OK']
        return response
        
class Organization_list(object):
    def __call__(self,request):
        self.request=request
        try:
            callbackmethod = getattr(Organization_list, "do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method = [m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self)
    def do_GET(self):
        json=serializers.serialize('json', Organization.objects.filter(exist_flag=True))
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response
        
    @login_required()
    def do_POST(self):
#        try:
            per_model=Organization.objects.organization_create(admin=self.auth_models,**json_to_kwarg(self.request.raw_post_data))
            if per_model==None:
                return HttpResponseBadRequest()
            pass
#        except Exception:
#            return HttpResponseBadRequest()
            org=Organization.objects.get(id=per_model.id)
            org.admin=self.auth_models
            org.save()
            json=serializers.serialize('json', [org])
            return HttpResponse(json,mimetype='application/json')

class Activity_user_detail():
    def __call__(self,request,activity_id,user_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1)
        self.user=get_object_or_404(User,id=user_id)
        try:
            callbackmethod=getattr(Activity_user_detail,'do_%s' % request.method)

        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
            pass
        return callbackmethod(self)
    def do_GET(self):
        activity_user=get_object_or_404(User_Activity,User=self.user,Activity=self.activity)
        json=serializers.serialize('json', [activity_user])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['ok']        
        return response
    @login_required()
    @admin_checked(urlmodel=True)
    def do_PUT(self):
        activity_user=get_object_or_404(User_Activity,User=self.user,Activity=self.activity)
        try:
            activity_user=update_from_json(activity_user, self.request.raw_post_data)
        except  AttributeError:
            response=HttpResponse()
            response.status_code=status_code['BAD REQUEST']
            return response
        else:
            json=serializers.serialize('json', [activity_user])
            response=HttpResponse(json,mimetype='application/json')
            response.status_code=status_code['OK']
            return response
    @login_required()
    @admin_checked(urlmodel=True)    
    def do_DELETE(self):
        activity_user=get_object_or_404(User_Activity,User=self.user,Activity=self.activity)
        activity_user.part_level=part_level_dic['participant_cancel']
        activity_user.save()
        response=HttpResponse()
        response.status_code=200
        return response
        
class Activity_tag_list(object):
    '''
    activity tag consoler
    '''
    def __call__(self,request,activity_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1)
        try:
            callbackmethod=getattr(Activity_tag_list, "do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self)    
    def do_GET(self):
        tag_list=self.activity.tag.filter(exsit_flag=True)
        json=serializers.serialize('json', tag_list)
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response
    @login_required()
    def do_POST(self):
        result_dict=json_to_kwarg(self.request.raw_post_data)
        tag=Activitytag.objects.create(result_dict)
        a_tag=Tag_Activity.objects.tag_act_create(activity=self.activity,tag=tag)
        json=serializers.serialize('json', [a_tag])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['CREATED']
        return response

        
        
        

class Activity_user_list(object):
    '''
    import funcation!!coming soon!!
    '''
    def __call__(self,request,activity_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1) 
        try:
            callbackmethod = getattr(Activity_detail, "do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method = [m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self) 
    def do_GET(self):
        raw_result=self.activity.participant.filter(**querydict_to_dict(self.request))
        a_u_list= get_partly_result(raw_result, self.request)
        json=serializers.serialize('json', a_u_list)
        response=HttpResponse(json,mimetype="application/json")
        response.status_code=status_code['OK']
        return response

class Activity_comment_list(object):
    '''
    list the comment_list of a Activity
    '''    
    def __call__(self,request,activity_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1)
        try:
            callbackmethod=getattr(Activity_comment_list, 'do_%s' % request.method)
            pass
        except AttributeError:
            allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self)
    def do_GET(self):
        activity_comments_raw=self.activity.comment_set.filter(exsit_flag=True,**querydict_to_dict(self.request))
        activity_comments=get_partly_result(activity_comments_raw, self.request)
        json=serializers.serialize('json', activity_comments)
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response
    
    @login_required()
    def do_POST(self):
        result_dict=json_to_kwarg(self.request.raw_post_data)
        comment=Comment.objects.comment_create(result_dict,activity=self.activity,user=self.auth_models)
        json=serializers.serialize('json', [Comment.objects.get(id=comment.id)])
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['CREATED']
        return response
class Comment_detail(object):    
        def __call__(self,request,comment_id):
            self.request=request
#            self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=True)
            self.comment=get_object_or_404(Comment,id=comment_id,exist_flag=True)
            try:
                callbackmethod=getattr(Comment_detail, 'do_%s' % request.method)
                pass
            except AttributeError:
                allowed_method=[m.lstrip('do_') for m in dir(self) if m.startswith('do_')]
                return HttpResponseNotAllowed(allowed_method)
            return callbackmethod(self)
        def do_DELETE(self):
            self.comment.exist_flag=False
            self.comment.save()
            response=HttpResponse()
            response.status_code=200
            return response
            
        
class Activity_organization_list(object):
    def __call__(self,request,activity_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1) 
        try:
            callbackmethod = getattr(Activity_detail, "do_%s" % request.method)
            pass
        except AttributeError:
            allowed_method = [m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self) 
    def do_GET(self):
        json=serializers.serialize('json', self.activity.host.filter(level__gt=host_level_dic['cancel_level']))
        response=HttpResponse(json,mimetype="application/json")
        response.status_code=status_code['OK']
        return response
    
class Activity_organization_detail(object):
    def __call__(self,request,activity_id,organization_id):
        self.request=request
        self.activity=get_object_or_404(Activity,id=activity_id,exist_flag=1)
        self.organization=get_object_or_404(Organization,id=activity_id,exist_flag=1)
        try:
            callbackmethod=getattr(Activity_organization_detail, "do_%s" %request.method)
            pass
        except AttributeError:
            allowed_method = [m.lstrip("do_") for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_method)
        return callbackmethod(self)
    def do_GET(self):
        json=serializers.serialize('json', get_object_or_404(Activity_Organization,activity=self.activity,organization=self.organization,level__gt=host_level_dic['cancel_level']))
        response=HttpResponse(json,mimetype='application/json')
        response.status_code=status_code['OK']
        return response
          
        
    
        
        
    
def test(request):
    '''
    测试用
    '''
    
    if request.method=="GET":
        print request.raw_post_data
    
        
            
        
          
            
          
