#-*- coding: UTF-8 -*-
from datetime import datetime

from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.crypto import constant_time_compare
from django.core.exceptions import ObjectDoesNotExist



# Create your models here.
part_level_dic = {'participant_ed':1, 'participant_ing':2, "participant_favor":3, "participant_cancel":0}
host_level_dic={'main_level':1,'second_level':2,'third_level':3,'cancel_level':0}
permission={'admin':1,'invaild':0}



def update_last_login(user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = datetime.now()
    user.save()

def set_password(raw_password):
    import random     
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hsh)

#加密
def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return constant_time_compare(hsh, get_hexdigest(algo, salt, raw_password))






class AccountManager(models.Manager):
    """
    the abstract class of a Account model Manager
    extend the class to customize Manager
    """
#    检查邮箱是否已经被注册
    def check_duplicate(self,account):
        try:
            models.Manager.get(self,account_email=account)
            pass
        except ObjectDoesNotExist:
            return True
        else:
            return False
        
    
# 账户创建    
    def account_create(self, **kwargs):
        
        try:
            if kwargs.get('password',None) is None or kwargs.get('account_email',None)  is None:
                return None
            if not self.check_duplicate(kwargs['account_email']):
                return None
            kwargs["password"] = set_password(kwargs["password"])
            if kwargs.get("account_email",None) is not None:
                try:
                    email_name, domain_part = kwargs["account_email"].strip().split('@', 1)
                except ValueError:
                    pass
                else:
                    kwargs['account_email'] = '@'.join([email_name, domain_part.lower()])
            kwargs["joined_time"] = datetime.now()
        except KeyError:
            return None
        else:
            return models.Manager.create(self, **kwargs)    

    
    


#class OrganizationManager(AccountManager):
#    """
#     Organizaiton Manager class
#    """
#    def organization_create(self, **kwargs):
#        return AccountManager.account_create(self, **kwargs)
#    
class UserManager(AccountManager):
    """
     User Manager class
    """
    def user_create(self, **kwargs):
        return AccountManager.account_create(self, **kwargs)    







        
class User(models.Model):
    account_email = models.EmailField(unique=True)
    sex=models.NullBooleanField()
    
    birthday=models.DateTimeField(null=True)
    university_name=models.CharField(max_length=30,null=True)
    university_year=models.IntegerField(max_length=11,null=True)
    university_department=models.CharField(max_length=30,null=True)
#    uid=models.CharField(max_length=10,unique=True)
    name = models.CharField(max_length=16)
#    email = models.EmailField()
    phone = models.CharField(max_length=15,null=True)
    head_url=models.URLField(null=True)
    personal_page = models.URLField(null=True)
    password = models.CharField(max_length=128)
#    department=models.CharField(max_length=30)
#    class_no=models.CharField(max_length=30)
    last_login = models.DateTimeField(null=True)
    joined_time = models.DateTimeField(default=datetime.now())
    #是否为组织方管理员    
    is_host=models.BooleanField(default=False)
    objects = UserManager()
    exist_flag=models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
    def check_password(self, raw_password):
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
                update_last_login(self)
            return is_correct
        update_last_login(self)
        return check_password(raw_password, self.password)
    def set_password(self, raw_password):
        self.password = set_password(raw_password)
        pass    
class OrganizationManager(models.Manager):
    def organization_create(self, **kwargs):
        if kwargs['admin']:
            return None
        kwargs['admin'].is_host=True
        kwargs['admin'].save()
        kwargs['create_time']=datetime.now()
        return models.Manager.create(self, **kwargs)    


    
class Organization(models.Model):
#    account = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField()
    url = models.URLField()
#    password = models.CharField(max_length=128)
#    last_login = models.DateTimeField()
    create_time = models.DateTimeField(default=datetime.now())
    admin=models.OneToOneField(User)
    objects=OrganizationManager()
    exist_flag=models.BooleanField(default=True)
    
    

    def __unicode__(self):
        return self.name
   
    def admin_list(self,**kwarg):
        return self.user_set.filter(**kwarg)
    
    
    def activity_list(self, **kwarg):
        return self.activity_set.filter(**kwarg)

class ActivtyManager(models.Manager):
    '''
    is not nessesary temporarily
    '''
    def activity_create(self, **kwargs):
        try:

            if kwargs.get("email",None) is not None:
                try:
                    email_name, domain_part = kwargs["email"].strip().split('@', 1)
                except ValueError:
                    pass
                else:
                    kwargs['email'] = '@'.join([email_name, domain_part.lower()])
        except KeyError:
            return None
        else:
            return models.Manager.create(self, **kwargs)     
        
        
class Location(models.Model):
    name=models.CharField(max_length=30)
    x=models.FloatField()
    y=models.FloatField()
    description=models.TextField()
    exist_flag=models.BooleanField()

class Activitytag(models.Model):
    label=models.CharField(max_length=14)
    exist_flag=models.BooleanField(default=True)

class Activity(models.Model):    
    name = models.CharField(max_length=255)
    description = models.TextField()
    b_date = models.DateTimeField()
    f_date=models.DateTimeField()
    addr=models.CharField(max_length=50)
    barcoder=models.IntegerField(max_length=15)
    location=models.ForeignKey(Location,null=True)
    timestamp = models.DateTimeField(default=datetime.now())
    url = models.URLField(null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=30,null=True)
    host = models.ManyToManyField(Organization, through='Activity_Organization')
    participant = models.ManyToManyField(User, through="User_Activity")
    tag=models.ManyToManyField(Activitytag,through='Tag_Activity')
    exist_flag=models.BooleanField(default=True)
    objects = ActivtyManager()
    
    def __unicode__(self):
        return self.name
    def check_desprate(self):
        return datetime.now() > self.date;
    def count_participant_ed(self):
        return self.participant.filter(part_level=part_level_dic["participant_ed"]).count()
    def count_participant_ing(self):
        return self.participant.filter(part_level=part_level_dic['participant_ing']).count()
    def count_participant_cancel(self):
        return self.participant.filter(part_level=part_level_dic['participant_cancel']).count()
    def count_participant_favor(self):
        return self.participant.filter(part_level=part_level_dic['paticipant_favor']).count()
    
    def count_tag(self):
        return self.tag.all().count()
    
    def check_tag(self):
        if self.count_tag()>5:
            return False
        return True
    def tag_list(self):
        return self.tag.all()
        
    def host_list(self, level=None):
        if level == None:
            return self.host.all()
        else:
            return self.host.filter(level=level)
    def paticipant_list(self, **kwarg):
        return self.participant.filter(**kwarg)
    def organization_list(self,**kwarg):
        return self.host.filter(**kwarg)

#作了点修改
#class Organization_User(models.Model):
#    user=models.ForeignKey(User)
#    organization=models.ForeignKey(Organization)
#    permission=models.IntegerField(max_length=2)
    
    
                
        
        
    
class Activity_Organization(models.Model):
    activity = models.ForeignKey(Activity)
    organization = models.ForeignKey(Organization)
    level = models.IntegerField(max_length=3)
    def __unicode__(self):
        return self.activty.name + ":" + self.organization.name
    pass





class User_Activity_Manager(models.Manager):
    def u_a_create(self, **kwargs):
        kwargs.setdefault('joined_time',datetime.now())       
        return models.Manager.create(self, **kwargs)
    
class User_Activity(models.Model):    
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    #包含exsit
    part_level = models.IntegerField()
    #参加后才能打分
    rate=models.IntegerField(max_length=3,default=0)
    joined_time=models.DateTimeField()
    objects=User_Activity_Manager()
    def __unicode__(self):
        return self.activity.name + ":" + self.user.name
    class Meta:
        unique_together=(('user','activity'),)

class Comment_Manager(models.Manager):
    def comment_create(self, **kwargs):
        if kwargs.get('user',None) is not None and kwargs.get('activity',None) is not None:
            kwargs['comment_date']=datetime.now()
            return models.Manager.create(self, **kwargs)

class Comment(models.Model):
    activity=models.ForeignKey(Activity)
    user=models.ForeignKey(User)
    comment_content=models.TextField()
    comment_date=models.DateTimeField(default=datetime.now())
    objects=Comment_Manager()
    exist_flag=models.BooleanField()
#待研究       
class User_Renren(models.Model):
    user=models.OneToOneField(User)
    renrenid=models.CharField(max_length=15)


class Tag_Activity_Manager():
    def tag_act_create(self,**kwargs):
        activity=kwargs.get('activity',None)
        tag=kwargs.get('tag',None)
        if activity  is not None and activity.checktag() and tag is not None :
            return models.Manager.create(self,**kwargs)
        else:
            return None
            
        
    
class Tag_Activity(models.Model):
    tag=models.ForeignKey(Activitytag)
    activity=models.ForeignKey(Activity)
    exist_flag=models.BooleanField(default=True)
    objects=Tag_Activity_Manager()
    
class Error(models.Model):
    error_code=models.IntegerField(max_length=10)
    error_name=models.CharField(max_length=128)
    error_desprition=models.TextField()
    
    def __unicode__(self):
        
        return self.error_name

#admin model register     
admin.site.register(Activity)
admin.site.register(Organization)
admin.site.register(Activity_Organization)
admin.site.register(User)
admin.site.register(Location)
admin.site.register(User_Activity)
admin.site.register(Comment)
admin.site.register(Activitytag)
admin.site.register(Tag_Activity)
admin.site.register(Error)
    
        
    
