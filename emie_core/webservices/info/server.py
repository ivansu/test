# coding:utf-8
import os
import sys


if __name__ == "__main__" :
    sys.path.insert(0, os.path.join('../../../'))

import datetime
from django.conf import settings
from django.db.models import F, Q

from web_edu.core.school.models import (
    InstitutionType, InstitutionVariant, School)
from web_edu.core.territory.models import Territory
from web_edu.emie_core.helpers import get_emie_info

from .SchoolInfoService_server import SchoolInfoService
from .SchoolInfoService_client import *


def date_soap(date):
    """
    преобразовать дату из питона в соап
    """
    dt = list(date.timetuple())
    dt[6] = 0
    return dt


def date_from_soap(dt):
    """
    преобразовать дату из соапа в питон
    """
    if dt:
        return datetime.date(dt[0], dt[1], dt[2])
    return None


def get_auth_token():
    """
    дать ауф токен
    """
    return getattr(settings, 'SOAP_AUTH_TOKEN', 'auth-token-of-school-ws')


class SchoolInfoServer(SchoolInfoService):
    def soap_listUnitTypesOper(self, ps, **kw):
        """
        получение списка типов
        """
        request = ps.Parse(listUnitTypesRequest.typecode)
        res = listUnitTypesResponse()
        q = []
        if request.AreaId:
            q = InstitutionType.objects.filter(school__territory__okato=request.AreaId)
        else:
            q = InstitutionType.objects.order_by('name')
        for type in q:
            r = res.new_returns()
            r.Id = type.id
            r.Name = type.name
            res.Returns.append(r)
        self.make_response_header(request, res)
        return request, res

    def soap_listUnitKindsOper(self, ps, **kw):
        """
        список kind
        """
        request = ps.Parse(listUnitKindsRequest.typecode)
        res = listUnitKindsResponse()
        q = InstitutionVariant.objects.order_by('name')
        if request.UnitType:
            q = q.filter(institutiontype=request.UnitType)
        for kind in q:
            r = res.new_returns()
            r.Id = kind.id
            r.Name = kind.name
            res.Returns.append(r)
        self.make_response_header(request, res)
        return request, res

    def soap_listUnitsOper(self, ps, **kw):
        """
        список школ
        """
        result = listUnitsResponse()
        request = ps.Parse(listUnitsRequest.typecode)
        schools = School.objects.select_related('ext_school')

        if any(request.Types):
            schools = schools.filter(institution_type__in=request.Types)
        if any(request.Kinds):
            schools = schools.filter(institution_variant__in=request.Kinds)
        if any(request.Areas):
            try:
                max_level = School.objects.latest('level').level
            except School.DoesNotExist:
                max_level = 0

            # Выбираем все учреждения у которых окато совпадают с переданными
            # или у которых есть родители с такими окато (sheet)
            okato_schools = Q(territory__okato__in=request.Areas)
            parent_okato_schools = Q(pk__isnull=True) # ничего

            for i in xrange(1, max_level + 1):
                parent_okato_schools |= Q(**{
                    ('parent__' * i) + 'territory__okato__in': request.Areas})

            schools = schools.filter(okato_schools | parent_okato_schools)

        for school in schools.order_by('name'):
            returns = result.new_returns()
            returns.Id = school.id
            returns.Name = school.name
            if school.ext_school and school.ext_school.liquidating:
                returns.Name += u' (Ликвидируется)'
            result.Returns.append(returns)

        self.make_response_header(request, result)
        return request, result

    def soap_unitsInfoOper(self, ps, **kw):
        """
        информация по школе
        """
        request = ps.Parse(unitsInfoRequest.typecode)
        res = unitsInfoResponse()
        units_list = request.Units
        if units_list == ['']:
            return request, res
        q = School.objects.filter(id__in=units_list).order_by('name')
        for school in q:
            r = res.new_returns()
            r.Id = school.id
            r.Name = school.name if school.name else u''
            r.Address = school.f_address_full if school.f_address_full else u''
            r.Telephone = school.telephone if school.telephone else u''
            r.Email = school.email if school.email else u''
            try:
                r.Web_page = school.ext_school.web_site if school.ext_school else ''
                r.Director = school.ext_school.director.person.fullname if\
                    school.ext_school and school.ext_school.director and\
                    school.ext_school.director.person else ''
            except Exception:
                r.Director = u''
                r.Web_page = u''
            res.Returns.append(r)
        self.make_response_header(request, res)
        return request, res

    def soap_unitDetailsOper(self, ps, **kw):
        """
        подробная информация про школу
        """
        request = ps.Parse(unitDetailsRequest.typecode)
        res = unitDetailsResponse()
        unit = request.Unit
        format = request.Format
        res.Returns, error_code, error_message = get_emie_info(
            unit, ps.request, format)
        self.make_response_header(request, res, error_code, error_message)
        return request, res

    def soap_listTerritoriesOper(self, ps, **kw):
        u"""Список территорий."""
        request = ps.Parse(listTerritoriesRequest.typecode)
        res = listTerritoriesResponse()

        # Получаем элементы первой вложенности от корневых папок и
        # все конечные элементы у которых нет родителя.
        query = Territory.objects.filter(
            Q(parent__isnull=True, rght=F('lft')+1) | Q(level=1)
        ).order_by('name')

        for territory in query:
            r = res.new_returns()
            r.Id = territory.id
            r.Name = territory.name
            r.Okato = territory.okato or u''
            res.Returns.append(r)
        self.make_response_header(request, res)
        return request, res

    def make_response_header(self, request, response, err_code=0, err_text=''):
        """
        создать ResponseHeader и заполнить его
        """
        response.ResponseHeader = response.new_responseHeader()
        response.ResponseHeader.ResponseDate = date_soap(datetime.datetime.now())
        response.ResponseHeader.RequestInitiatorCode = response.ResponseHeader.new_requestInitiatorCode()
        response.ResponseHeader.RequestInitiatorCode.RegionCode = '16'
        response.ResponseHeader.RequestInitiatorCode.ServiceOrgCode = 'school service code'


        if request.RequestHeader:
            response.ResponseHeader.RequestIDRef = request.RequestHeader.RequestId
        else:
            response.ResponseHeader.RequestIDRef = ''
        response.ResponseHeader.Error = response.ResponseHeader.new_error()
        response.ResponseHeader.Error.ErrorCode = err_code
        response.ResponseHeader.Error.ErrorMessage = err_text

        response.ResponseHeader.AuthToken = get_auth_token()

if __name__ == "__main__" :
    from ZSI.ServiceContainer import AsServer
    AsServer(8000, (SchoolInfoServer('webservices/unitkinds'),))
