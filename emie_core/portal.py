#coding:utf-8
"""
Функционал для подготовки портальных отображений

@author: akvarats
"""

import json
import os

from django import template as django_templates
from django.conf import settings

from web_edu.livesettings import config
from web_edu.core.classyear.models import ClassYear
from web_edu.core.school.models import School
from web_edu.plugins.emie_school.models import SchoolEduProcessStudyPlan
from web_edu.core.fgos.helpers import fgos_is_used


class EmiePortalViewRenderer(object):
    """
    Класс, который инкапсулирует рендеринг портального
    представления расширенной информации обучреждении
    """
    def __init__(self, template='emie-base-view-markup.html'):
        """
        Типа, конструктор
        @param template: имя темплейта, который используется при рендеринге
        """
        self.template = template

    def prepare_context(self, school=None, request_data=None):
        """
        Метод подготовки контекста рендеринга темплейта
        """
        pass

    def render_markup(self, school=None, request_data=None, request=None,
                      format=None, params=None):
        """
        Данный метод может быть переопределен в дочерних классах.

        @param school: объект учреждения,
            по которому выводится подробная информация
        @param request_data: объект,
            в котором упакованы все параметры POST запроса,
            ответ на который выполняется
        """
        data = {
            'school': school,
            'current_site': config.SITE_URL,
            'request': request_data,
            'static': settings.MEDIA_URL,
        }
        params = params or {}
        
        data['is_smev'] = params.get('is_smev')

        if school:
            school = school[0]
            plans = [
                {'name': p.display(), 'file': p.file.url} for p in
                SchoolEduProcessStudyPlan.objects.filter(
                    curriculum__school=school, show=True, file__isnull=False
                )
            ]
            splans = json.dumps(plans)

            work_programs = school.schooleduprocessworkprogram_set.filter(
                show=True)
            if params.get('class_year'):
                work_programs = work_programs.filter(
                    study_level__in=ClassYear.objects.filter(
                        id=params.get('class_year')
                    ).values_list('study_level_id', flat=True)
                )

            subject = params.get('subject')
            if subject:
                if fgos_is_used():
                    work_programs = work_programs.filter(discipline=subject)
                else:
                    work_programs = work_programs.filter(subject=subject)

            if (
                school.institution_type and school.institution_type.pk == (
                    School.INSTITUTION_TYPE_PK_FUTHER_EDU)
            ):
                data['study_plans_files'] = [
                    {'name': f.name, 'file': f.file} for f in
                    school.schooleduprocessstudyplanfile_set.filter(show=True)
                ]

            data.update({
                'study_plans': splans,
                'study_plans_arr': plans,
                'work_programs': work_programs,
                'site_url': config.SITE_URL,
                'year_graphs': (
                    school.schooleduprocessyeargraph_set.filter(show=True)),
                'accreditations': school.accreditation_set.filter(show=True),
                'licenses': school.license_set.filter(show=True),
                'norm_docs': school.schoolnormdoc_set.filter(vop=True),
                'ustav_file_name': (
                    os.path.basename(school.ext_school.ustav_file.name) if
                    school.ext_school and school.ext_school.ustav_file and
                    school.ext_school.ustav_file.name
                    else u''),
                'fgos_is_used': fgos_is_used()
            })
        if request:
            context = django_templates.RequestContext(request, data)
        else:
            context = django_templates.Context(data)
        if format == 'json':
            self.template = 'emie-base-view-markup.json'
        t = django_templates.loader.get_template(self.template)
        return t.render(context)


class EmiePortal404Renderer(EmiePortalViewRenderer):
    """
    Класс, который вместо информации об учреждении рендерит 404 ошибку
    """
    def __init__(self):
        super(EmiePortal404Renderer, self).__init__(
            template='emie-404-markup.html')
