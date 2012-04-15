import os
import sys
 

path = '/home/ryanhust/python/Barcoder/src'
if path not in sys.path:
    sys.path.append(path)
    
    

 

os.environ['DJANGO_SETTINGS_MODULE'] = 'Barcoder.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
