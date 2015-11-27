#coding:utf-8
"""
Created on 07.11.2010

@author: akvarats
"""

from django.conf import urls
from helpers import default_extender_info
from m3 import plugins

from ui import EmieActionPack
from web_edu.core.users.decorators import authenticated_user_required
from web_edu.controllers import dict_controller
from web_edu.emie_core.ui import EmieTeacherSelectPack
from web_edu.emie_core.webservices.info.actions import SoapInfoActionPack


@authenticated_user_required
def emie_view(request):
    """
    Основная вьюха приложения emie_core
    """
    return dict_controller.process_request(request)


def register_actions():
    """
    Регистрация паков и действий приложения
    """
    dict_controller.packs.append(EmieActionPack())
    dict_controller.packs.append(EmieTeacherSelectPack())
    from web_edu.webservice.app_meta import ws_controller
    ws_controller.packs.append(SoapInfoActionPack())


def register_extensions():
    """
    Регистрирует точки расширения
    """
    #===========================================================================
    # Регистрируем основную точку расширения, которая возвращает полную информацию
    #
    #===========================================================================
    handler = plugins.ExtensionHandler(handler=default_extender_info, call_type=plugins.ExtensionHandler.INSTEAD_OF_PARENT)
    point = plugins.ExtensionPoint(name='emie.ext-info', default_listener=handler)
    plugins.ExtensionManager().register_point(point)


def register_urlpatterns():
    """
    Регистрация конфигурации урлов для приложения
    """
    return urls.defaults.patterns('',
        (r'^emie/', emie_view),
    )

