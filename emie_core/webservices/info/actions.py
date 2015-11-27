# -*- coding: utf-8 -*-

from m3.actions import ActionPack

from web_edu.emie_core.webservices.info.server import SchoolInfoServer
from web_edu.m3_backports.soapcontroller import SOAPAction


class SoapInfoActionPack(ActionPack):
    """Экшн пак сервиса info"""

    def __init__(self):
        super(SoapInfoActionPack, self).__init__()
        self.actions.append(SOAPAction(SchoolInfoServer, '/info'))