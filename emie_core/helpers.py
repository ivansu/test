#coding:utf-8
"""
Created on 07.11.2010

@author: akvarats
"""
from django.shortcuts import render_to_response
from django.db.models.query_utils import Q

from m3 import plugins
from m3 import actions

from web_edu.core.users.models import UserProfile
from web_edu.core.school.models import School
from web_edu.core.territory.models import Territory
from web_edu.core.teacher.models import TeacherPortfolio

def sequenced_run(f):
    """
    Декоратор, которым необходимо оборачивать вызовы хендлеров в плагинах
    """
    def action(school, *args, **kwargs):
        """
        Действие декоратора
        """
        prev_result = kwargs['ext_result'] # результат отработки других плагинов
        if prev_result:
            return prev_result
        return f(school, *args, **kwargs)
    return action

class ExtenderInfo(object):
    """
    Класс, который описывает расширенную информацию о модели School,
    предоставляемую плагином. На основе этой "метаинформации" производится
    выполнение кода соответствующих плагинов.
    """
    def __init__(self):
        self.related_name = ''
        self.markup_renderer = None
        self.extender_model = None
        self.edit_window = None

def default_extender_info(school=None, *args, **kwargs):
    """
    Дефолтный обработчик получения расширенной информации по модели School
    """
    return ExtenderInfo() if len(plugins.ExtensionManager().get_handlers('emie.related-name')) == 1 else None

def get_emie_info(school_id, request, format='html'):
    res = None
    error_code = 0
    error_message = ''
    try:
        # выполняем первоначальную прогрузку объекта
        school = School.objects.get(id=school_id)

        #разбиваем учителей в школе на группы Администрация
        #и Педагогический состав
        teachers = school.teacher_set.all()
        adm_teachers = []
        ped_teachers = []
        for teacher in teachers:
            teacher_is_administration = False
            q = teacher.person.userprofile_set.filter(
                metarole=UserProfile.TEACHER, school=teacher.school).all()
            if len(q) > 0:
                teacher.profile = q[0]
            else:
                teacher.profile = None

            try:
                portfolio = teacher.person.teacherportfolio
            except TeacherPortfolio.DoesNotExist:
                teacher.category = ''
            else:
                teacher.category = portfolio.category_display()

            for t_job in teacher.jobs():
                if t_job.job.type == 1:
                    teacher_is_administration = True
            if teacher_is_administration:
                adm_teachers.append(teacher)
            else:
                ped_teachers.append(teacher)

        # получаем описание расширенной информации по учреждению
        ext_info = plugins.ExtensionManager().execute('emie.ext-info', school=school)
        # выполняем прогрузку объекта с расширенной информацией
        school = School.objects.filter(id=school_id).select_related(ext_info.related_name)
        school.ped_teachers = ped_teachers
        school.adm_teachers = adm_teachers
        # строим объект рендерера
        renderer = ext_info.markup_renderer
        res = unicode(renderer.render_markup(
            school, request=request, format=format))
    except School.DoesNotExist:
        error_code = -1
        error_message = u'Учреждение с указанным id не существует!'
    return res, error_code, error_message


def get_territories_by_type_and_kind(types, kinds):
    """
    Получение списка территорий учреждений по видам и типам
    """
    q = Territory.objects.order_by('name').distinct()
    if types != ['']:
        fltr1 = Q(**{'school__institution_type__in': types})
    else:
        fltr1 = Q(**{'school__institution_type__isnull': False})
    if kinds != ['']:
        fltr2 = Q(**{'school__institution_variant__in': kinds})
    else:
        fltr2 = Q(**{'school__institution_variant__isnull': False})
    return q.filter(fltr1 & fltr2)
