'''
Created on 2012-4-8

@author: ryanhust
'''
from django.http  import HttpResponse  as Response
from Barcoder.service.models import Error
from django.core import serializers


class HttpResponseError(Response):
    '''
    Error Response when an Error occurs
    '''


    def __init__(self,status_code,error_code):
        '''
        Constructor
        '''
        
        error=Error.objects.filter(error_code=error_code)
        json=serializers.serialize('json', error)
        Response.__init__(self,json,mimetype='application/json')
        self.status_code=status_code