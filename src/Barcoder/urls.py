from django.conf.urls.defaults import patterns, include, url
from service.views import *

from service.views import test
from django.contrib import admin
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Barcoder.views.home', name='home'),
    # url(r'^Barcoder/', include('Barcoder.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
    (r'^activity/([\w-]+)/$',Activity_detail()),
    (r'^activity/([\w-]+)/comments/',Activity_comment_list()),   
    (r'^activity/([\w-]+)/user/([\w-]+)/',Activity_user_detail()),
    (r'^activity/([\w-]+)/users/',Activity_user_list()),
    (r'^activity/([\w-]+)/tags/',Activity_tag_list()),
    (r'^activities/',Activty_list()),
    (r'^organizations/',Organization_list()),
    (r'^activity/([\w-]+)/organizations/',Activity_organization_list()),
    (r'^activity/([\w-]+)/organization/([\w-]+)/',Activity_organization_detail()),
    (r'^organization/([\w-]+)/activities/',Organization_activity_list()),
    (r'^organization/([\w-]+)/admins/',Organization_admin_list()),
    (r'^organization/([\w-]+)/admin/([\w-]+)/',Organization_admin_detail()),
    (r'^organization/([\w-]+)/activity/([\w-]+)/',Organization_activity_detail()),
    (r'^organization/([\w-]+)/$',Organization_detail()),
    (r'^users/',User_list()),
    (r'^user/([\w-]+)/$',User_detail()),
    (r'^user/([\w-]+)/activities/',User_activity_list()),
    (r'^user/([\w-]+)/activity/([\w-]+)/',User_activity_detail()),
    
    
    
    (r'^test/',test),
    
)
