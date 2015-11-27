#coding:utf-8
from m3 import ApplicationLogicExceptionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
"""
Реализует базовый уровень пользовательского интерфейса для подсистемы
заполнения данных учреждения.

Created on 07.11.2010

@author: akvarats
"""
import datetime

from m3 import ApplicationLogicException
from m3 import plugins
from m3_legacy.logger import logging
from m3 import actions
from m3_legacy.logger import logging
from m3_ext.ui.results import ExtUIScriptResult

import objectpack
from objectpack.exceptions import ValidationError

from web_edu.core.helpers import get_current_school
from web_edu.core.school.models import School
from web_edu.core.schoolchild.models import SchoolChild
from web_edu.core.teacher.actions import TeacherSelectPack
from web_edu.core.teacher.models import Teacher
from web_edu.core.users import employer_roles as roles

from portal import EmiePortal404Renderer


#===============================================================================
# Действия
#===============================================================================


class EmieActionPack(actions.ActionPack):
    """
    Кипер основных действий подсистемы
    """
    url = '/ui'

    def __init__(self):
        super(EmieActionPack, self).__init__()
        self.emie_save_action = EmieSaveAction()
        self.emie_view_markup_action = EmiePortalViewAction()
        self.emie_window_action = EmieWindowAction()
        self.actions = [
            self.emie_window_action,
            self.emie_view_markup_action,
            self.emie_save_action
        ]


class EmieTeacherSelectPack(TeacherSelectPack):
    """
    Пак выбора руководителя с сортировкой по школе,
    без учёта дочерних школ
    """

    url = '/teacher-select'

    _is_primary_for_model = False

    def get_rows_query(self, request, context):
        return super(EmieTeacherSelectPack, self).get_rows_query(
            request, context
        ).filter(school=get_current_school(request))


class EmieWindowAction(actions.Action):
    """
    Действие на отображение дополнительной информации по учреждению
    """

    url = '/edit-window'
    shortname = 'EmieWindowAction'
    perm_code = 'view'

    def run(self, request, context):
        """
        """
        # 1. получаем объект учреждения из параметров пользователя
        user_school = get_current_school(request)
        if not user_school:
            return actions.OperationResult(success=False,
                message=u'Вы не можете заполнить данные учреждения, потому как \
                для Вашего пользователя оно не задано<br><br>Обратитесь к \
                администратору системы за дальнейшими разъяснениями.')



        # 2. получаем метаинформацию по расширению из плагина при помощи вызова
        #   хендлера точки расширения
        ext_info = plugins.ExtensionManager().execute('emie.ext-info', school=user_school)

        if not ext_info or not ext_info.related_name or not ext_info.edit_window:
            return actions.OperationResult(success=False,
                message=u'Вы не можете заполнить данные учреждения, потому как не \
                удалось получить расширенную модель информации.<br><br>Обратитесь к \
                администратору системы за дальнейшими разъяснениями.')

        # 3. читаем объект учреждения повторно с учетом связанной модели
        #current_school = School.objects.filter(id=user_school.id).select_related(ext_info.related_name)[0]
        current_school = School.objects.get(id=user_school.id)

        # 4. выполняем метод окна для реализации
        # контекстнозависимого интерфейса, если он присутствует у окна
        extender = getattr(ext_info.edit_window, 'apply_request', None)
        if extender and callable(extender): extender(request, context)

        ext_info.edit_window.form.url = self.parent.emie_save_action.get_absolute_url()

        try:
            ext_info_object = ext_info.extender_model.objects.get(
                                **{ext_info.extender_model._mie_meta.primary_field:current_school.id})
            ext_info.edit_window.form.from_object(ext_info_object)
        except ext_info.extender_model.DoesNotExist:
            pass

        ext_info.edit_window.form.from_object(current_school)
        context.school_id = current_school.id

        if not roles.user_has_permission(request.user.get_profile(), roles.PERM_EMIE_SCHOOL_EDIT):
            ext_info.edit_window.make_read_only()

        # Вызов точки расширения плагина tumen_sync_units. обработчик данной
        # точки расширения добавляет поля "Форма собственности",
        # "Организационная форма" и "Тип учреждения" в форму редактирования
        # данных учреждения на вкладку "Общая информация" > "Дополнительная
        # информация" (см. задачу 81555).
        plugins.ExtensionManager().execute(
            'web_edu.plugins.tymen_sync_units.extend_form',
            current_school,
            ext_info.edit_window)

        return ExtUIScriptResult(ext_info.edit_window)


class EmieSaveAction(objectpack.BaseWindowAction):
    """
    Действие на сохранение расширенной модели информации по учреждению
    """

    url = '/save'

    def context_declaration(self):
        return [
            actions.ACD(name='school_id', type=int, required=True,
                        verbose_name=u'id учреждения'),
            actions.ACD(name='liquidating', type=unicode, required=True,
                        default=u'off', verbose_name=u'Дата ликвидации'),
            actions.ACD(name='liquid_date', type=datetime.date, required=True,
                        default=datetime.date.today(),
                        verbose_name=u'Дата ликвидации'),
        ]

    @staticmethod
    def _get_remaining_persons(context):
        u"""
        Возвращает сотрудников и учеников, для передачи данных в стор.
        """

        current_school = School.objects.get(id=context.school_id)

        employees = []
        pupils = []

        if context.liquidating == u'on':
            # Не уволенные, до даты ликвидации, сотрудники
            employees_data = Teacher.objects.filter(
                school=current_school, discharge_reason__isnull=True,
                info_date_end__gte=context.liquid_date
            ).select_related(
                'person'
            ).values('person__id', 'person__fullname', 'person__date_of_birth')

            # Не отчисленные, до даты ликвидации, ученики
            pupils_data = SchoolChild.objects.filter(
                school=current_school, graduate_reason__isnull=True,
                info_date_end__gte=context.liquid_date
            ).select_related(
                'person'
            ).values('person__id', 'person__fullname', 'person__date_of_birth')

            def prepare_list_data(values_query_set):
                u"""
                Сериализует ValuesQuerySet в список кортежей,
                добавляя дату в виде строки.
                """
                values = []
                for value in values_query_set:
                    values.append((
                        value['person__id'],
                        value['person__fullname'],
                        value['person__date_of_birth'].strftime('%d.%m.%Y')
                        if value['person__date_of_birth'] else ''
                    ))

                return values

            if employees_data.exists():
                employees = prepare_list_data(employees_data)

            if pupils_data.exists():
                pupils = prepare_list_data(pupils_data)

            return employees, pupils

    def run(self, request, context):
        """
        """

        if not roles.user_has_permission(request.user.get_profile(), roles.PERM_EMIE_SCHOOL_EDIT):
            raise ApplicationLogicException(u'У вас нет прав для выполнения этого действия')

        # 1. получаем расширенную информацию
        try:
            current_school = School.objects.get(id=context.id)
        except School.DoesNotExist:
            return actions.OperationResult(success=False,
                                message=u'Не удалось сохранить изменения.\
                                <br>Объект учреждения не найден в базе данных.')

        ext_info = plugins.ExtensionManager().execute('emie.ext-info', school=current_school)
        if not ext_info or not ext_info.related_name or not ext_info.edit_window:
            return actions.OperationResult(success=False,
                        message=u'Не удалось сохранить изменения.<br>\
                        Не найдено описание расширенных свойств объекта учреждения.')

        current_school = School.objects.filter(id=context.id).select_related(ext_info.related_name)[0]

        # забираем объект расширенной информации из модели школы.
        # если связанного объекта с расширенной информацией нет,
        # то мы создаем такой объект
        extender_object = getattr(current_school, ext_info.related_name, None)
        if not extender_object:
            # создаем объект расширенной информации
            extender_object = ext_info.extender_model()
            # ставим в объекте расширенной информации ссылку
            setattr(extender_object, ext_info.extender_model._mie_meta.primary_field, current_school)
            # проставляем в объект school ссылку на extender_object для обеспечения
            # корректного биндинга формы
            # setattr(current_school, ext_info.related_name, extender_object)

        try:
            ext_info.edit_window.form.bind_to_request(request)

            school_id = current_school.id
            extender_id = extender_object.id

            ext_info.edit_window.form.to_object(current_school)
            ext_info.edit_window.form.to_object(extender_object)

            #Todo Не записывает галочки через ext_info.edit_window.form.to_object(extender_object)
            #Todo запись напрямую
            if request.REQUEST.get('work_programs_vop2') == 'true':
                extender_object.work_programs_vop = True
            else:
                extender_object.work_programs_vop = False
            if request.REQUEST.get('year_graphs_vop2') == 'true':
                extender_object.year_graphs_vop = True
            else:
                extender_object.year_graphs_vop = False
            if request.REQUEST.get('study_plans_vop2') == 'true':
                extender_object.study_plans_vop = True
            else:
                extender_object.study_plans_vop = False

            # это пиздец! почему у нас так биндинг форм работает??
            current_school.id = school_id
            extender_object.id = extender_id

            setattr(extender_object, ext_info.extender_model._mie_meta.primary_field, current_school) # это всё уебищные названия полей
            try:
                current_school.save()
            except ValidationError as e:
                raise ApplicationLogicException(unicode(e))
            extender_object.save()

            self.handle('post_save', (extender_object, context))
        except:
            raise

            logging.exception(u'Не удалось сохранить объект учреждения')
            return actions.OperationResult(success=False,
                    message=u'Не удалось сохранить расширенные данные по учреждению<br>\
                    <br>Подробности в логах системы.')

        if getattr(context, 'not_liquidate', None):
            # Если есть сотрудники или ученики не уволенные/отчисленные до даты
            # ликвидации, то отмена ликвидации учреждения.
            extender_object.liquidating = False
            extender_object.liquid_date = None
            extender_object.save()

        return actions.OperationResult()


class EmiePortalViewAction(actions.Action):
    """
    Действие на получение html-кода для отображения информации
    """

    url = '/view-markup'

    def context_declaration(self):
        """
        Для выполнения действия необходимо иметь school_id
        """
        return [actions.ActionContextDeclaration(name='school_id', type=int, required=True, default=0), ]

    def run(self, request, context):
        """
        """
        renderer = EmiePortal404Renderer()
        if context.school_id > 0:
            try:
                # выполняем первоначальную прогрузку объекта
                school = School.objects.get(id=context.school_id)
                # получаем описание расширенной информации по учреждению
                ext_info = plugins.ExtensionManager().execute('emie.ext-info', school=school)
                # выполняем прогрузку объекта с расширенной информацией
                school = School.objects.filter(id=context.school_id).select_related(ext_info.related_name)
                # строим объект рендерера
                renderer = ext_info.markup_renderer
            except School.DoesNotExist:
                pass
            except:
                logging.exception(u'Не удалось получить объект School с id=' + str(context.school_id) + u' из базы данных.')
        return actions.TextResult(renderer.render_markup(school, request=request))

