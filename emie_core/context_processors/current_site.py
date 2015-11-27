#coding:utf-8
"""
Created on 16.12.2010

@author: kirov
"""
from django.conf import settings
from django.contrib.sites.models import Site

def current_site(request):
    """
    A context processor to add the "current site" to the current Context
    """
    if request.is_secure():
        current_site = 'https://%s' % request.get_host()
    else:
        current_site = 'http://%s' % request.get_host()
    return { 'current_site': current_site }
