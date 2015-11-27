#coding:utf-8
"""

Created on 29.12.2010

@author: sabitov
"""
from django.conf import settings
from m3_ext.ui.windows import ExtEditWindow
from m3_ext.ui.controls import ExtButton
from m3_ext.ui.panels import ExtPanel, ExtForm
from m3_ext.ui.fields import (
    ExtCheckBox, ExtStringField, ExtTextArea,
    ExtNumberField, ExtDictSelectField, ExtHiddenField)
from m3_ext.ui.containers import ExtFieldSet, ExtTabPanel, ExtContainer
from m3_fias.addrfield import ExtFiasAddrComponent
from m3_ext.ui.fields import ExtDisplayField
from m3_ext.ui.fields.complex import ExtFileUploadField, ExtImageUploadField
from m3_ext.ui import all_components as ext
from m3.actions import urls
from web_edu.emie_core.ui import EmieTeacherSelectPack

#===============================================================================
# Интерфейсные элементы
#===============================================================================


class BaseEmieWindow(ExtEditWindow):
    """
    Базовое окно подсистеме EMIE.

    От данного окна должны наследоваться все окна, которые расширяют модель учреждения.
    """

    def make_read_only(self, *args, **kwargs):
        super(BaseEmieWindow, self).make_read_only()
        self._ur_address.read_only = True
        self._fact_address.read_only = True

    def _new_visibility_checkbox(self, name, label=None):
        chk = ExtCheckBox(label=label or u'Отображать на портале',
            name=name)
        self._visibility_checkboxes.append(chk)
        setattr(self, name, chk)
        return chk

    def __init__(self, *args, **kwargs):
        super(BaseEmieWindow, self).__init__(*args, **kwargs)

        self._visibility_checkboxes = []


        self.width = 700
        self.height = 500
        self.maximizable = True
        self.minimizable = True
        self.closable = True
        self.maximized = True
        self.title = u'Данные моего учреждения'
        self.template_globals = 'emei-base-edit-window.js'
        self.body_cls = 'x-window-mc'

        self.layout = 'fit'
        self.form = ExtForm(layout='border', file_upload=True)

        id = ExtHiddenField(name='id')

        # Шапка
        self.name_field = ExtStringField(label=u'Наименование',
            name='name', anchor='100%', max_length=300)

        self.foto = ExtImageUploadField(name="foto", label=u"Фотография",
            width=300)

        self.director = ExtDictSelectField(
            name='director_id',
            label=u'Руководитель',
            display_field='fullname',
            hide_edit_trigger=True
        )
        self.director.pack = EmieTeacherSelectPack

        self.tabs_panel = ExtContainer(region='center', layout='fit')
        self.tabs = ExtTabPanel(region='center', width=100,
            deferred_render=True)
        self.tabs_panel.items.append(self.tabs)

        # Вкладка контактная информация
        self.tab_main0 = self._new_tab(u'Контактная информация')

        self._add_field_set(self.tab_main0, u'Информация',
            ExtStringField(label=u'Телефон', name='telephone', mask_re='[0-9-]'),
            ExtStringField(label=u'Эл. почта', name='email', vtype='email'),
            ExtStringField(label=u'Сайт', name='web_site'), #TODO: в модели School этого поля нет. Необходимо добавить.
            ExtStringField(label=u'Расположение на карте', name='location'), #TODO: в модели School этого поля нет. Необходимо добавить.
        )

        self._fact_address = ExtFiasAddrComponent(
            anchor='100%',
            level=ExtFiasAddrComponent.HOUSE,
            place_field_name='f_address',
            street_field_name='f_address_street',
            house_field_name='f_address_house',
            corps_field_name='f_address_corps',
            addr_field_name='f_address_full',
            use_corps=True,
            height=125
        )

        self.faddr_fieldset = self._add_field_set(
            self.tab_main0,
            u'Фактический адрес',
            self._fact_address
        )
        self.faddr_fieldset.height = 165

        self._ur_address = ExtFiasAddrComponent(
            anchor='100%',
            level=ExtFiasAddrComponent.HOUSE,
            place_field_name='u_address',
            street_field_name='u_address_street',
            house_field_name='u_address_house',
            corps_field_name='u_address_corps',
            addr_field_name='u_address_full',
            use_corps=True,
            height=125
        )

        self.uaddr_fieldset = self._add_field_set(
            self.tab_main0,
            u'Юридический адрес',
            self._ur_address
        )
        self.uaddr_fieldset.height = 165

        # Вкладка Правовые акты
        self.tab_main1 = self._new_tab(title=u'Нормативно-правовые акты',
            layout='vbox')
        #ustav_panel = ext.ExtPanel(width=500, layout='form')#anchor='100%'
        #self.tab_main1.items.append(ustav_panel)
        self.tab_main1.layout_config = {'align': 'stretch'}

        self._add_field_set(self.tab_main1, u'Устав',
            ExtFileUploadField(name='ustav_file', label=u'Документы',
               anchor='90%', possible_file_extensions=settings.EXTENSIONS),
            self._new_visibility_checkbox('ustav_vop')
        )

        self.norm_doc_grid = ext.ExtObjectGrid(flex=1, anchor='100%', cls='fix-search-bar')
        self.tab_main1.items.append(self.norm_doc_grid)
        pack = urls.get_pack_instance('SchoolNormDocPack')
        pack.configure_grid(self.norm_doc_grid)

        # Вкладка Лицензия и аккредитация
        self.tab_main2 = self._new_tab(title=u'Лицензия и аккредитация')

        self._add_field_set(self.tab_main2,
            u'Информация об имеющихся лицензиях',
            ExtTextArea(label=u'Информация об имеющихся лицензиях',
                name='license_info', anchor='100%'),
            ExtFileUploadField(name='license_file', label=u'Документы',
                width=300),
            self._new_visibility_checkbox('license_vop')
        )

        self._add_field_set(self.tab_main2, u'Информация об аккредитации',
            ExtTextArea(label=u'Информация об аккредитации',
                name='akkred_info', anchor='100%',),
            ExtFileUploadField(
                name='akkred_file',
                label=u"Документы",
                width=300,
            ),
            self._new_visibility_checkbox('akkred_vop')
        )

        # Вкладка Язык обучения
        self.tab_main3 = self._new_tab(title=u'Язык обучения')

        self._add_field_set(self.tab_main3,
            u'Язык (языки), на котором ведутся обучение и воспитание',
            ExtTextArea(label=u'Языки', name='language_info', anchor='100%',),
            self._new_visibility_checkbox('language_vop')
        )

        # Вкладка Планируемые показатели приема
        self.tab_main4 = self._new_tab(title=u'Планируемые показатели приема')

        self._add_field_set(self.tab_main4, u'Планируемое количество классов',
            ExtNumberField(label=u'Количество', name='class_count_info'),
            self._new_visibility_checkbox('class_count_vop')
        )

        self.fs_plan_reception = self._add_field_set(self.tab_main4,
            u'Планируемые показатели приема на следующий учебный год в ОУ',
            ExtDisplayField(value=(
                u'Информация о планируемых показателях приема' +
                u' на следующий учебный год в ОУ')),
            ExtTextArea(label=u'Информация',
                name='projected_rates_info', anchor='100%'),
            self._new_visibility_checkbox('projected_rates_vop')
        )

        # Вкладка Свободные места
        self.tab_main5 = self._new_tab(title=u'Свободные места')

        self._add_field_set(self.tab_main5,
            u'Информация о наличии свободных мест в классах',
            ExtDisplayField(
                value=u'Информация о наличии свободных мест в классах'),
            ExtTextArea(label=u'Информация',
                name='availability_class_info', anchor='100%',),
            self._new_visibility_checkbox('availability_class_vop')
        )

        self._add_field_set(self.tab_main5,
            u'Свободные места: группы продленного дня',
            ExtDisplayField(value=(u'Информация о наличии свободных мест ' +
                u'в группах продленного дня')),
            ExtTextArea(label=u'Информация',
                name='availability_group_info', anchor='100%',),
            self._new_visibility_checkbox('availability_group_vop')
        )

        self._add_field_set(self.tab_main5,
            u'Свободные места: компенсирующее обучение',
            ExtDisplayField(value=(u'Информация о наличии свободных мест ' +
                u'в классах компенсирующего обучения')),
            ExtTextArea(label=u'Информация',
                name='availability_class_comp_info', anchor='100%',),
            self._new_visibility_checkbox('availability_class_comp_vop')
        )

        # Вкладка Зачисление в ОУ
        self.tab_main6 = self._new_tab(title=u'Зачисление в ОУ')

        self._add_field_set(self.tab_main6,
            (u'Перечень документов, предоставление ' +
            u'которых необходимо для зачисления в ОУ'),
            ExtTextArea(label=u'Информация',
                name='enrollment_docs_in_ou_info', anchor='100%'),
            ExtFileUploadField(name='enrollment_docs_in_ou_file',
                label=u"Документы", anchor='90%',
                possible_file_extensions=settings.EXTENSIONS),
            self._new_visibility_checkbox('enrollment_docs_in_ou_vop')
        )

        # Вкладка Продолжительность обучения
        self.tab_main7 = self._new_tab(
            title=u'Продолжительность обучения и режим занятия')

        self._add_field_set(self.tab_main7,
            (u'Продолжительность обучения на каждом ' +
            u'этапе обучения и возраст воспитанников'),
            ExtTextArea(label=u'Информация', name='durations_info',
                anchor='100%',),
            self._new_visibility_checkbox('durations_vop')
        )

        self._add_field_set(self.tab_main7,
            u'Режим занятий обучающихся, воспитанников',
            ExtTextArea(label=u'Информация',
                name='mode_employment_info', anchor='100%',),
            self._new_visibility_checkbox('mode_employment_vop')
        )

        # Вкладка Отчисления
        self.tab_main8 = self._new_tab(title=u'Отчисление')

        self._add_field_set(self.tab_main8,
            u'Порядок и основания отчисления обучающихся, воспитанников',
            ExtTextArea(label=u'Информация',
                name='deduction_info', anchor='100%',),
            self._new_visibility_checkbox('deduction_vop')
        )

        # Вкладка Доп. услуги
        self.tab_main9 = self._new_tab(title=u'Доп. услуги')

        self._add_field_set(self.tab_main9,
            u'Наличие дополнительных образовательных услуг',
            ExtDisplayField(value=(
                u'Наличие дополнительных образовательных услуг, ' +
                u'в том числе платных образовательных услуг, и порядок ' +
                u'их предоставления (на договорной основе)')),
            ExtTextArea(label=u'Информация',
                name='additional_services_info', anchor='100%'),
            self._new_visibility_checkbox('additional_services_vop')
        )

        # Вкладка Система оценок
        self.tab_main10 = self._new_tab(title=u'Система оценок')

        self._add_field_set(self.tab_main10,
            u'Система оценок',
            ExtDisplayField(value=(u'Система оценок, формы, порядок и ' +
            u'периодичность промежуточной аттестации обучающихся')),
            ExtTextArea(label=u'Информация',
                name='rating_system_info', anchor='100%'),
            self._new_visibility_checkbox('rating_system_vop')
        )

        # Вкладка Сведения о коррекционных учреждениях
        self.tab_main11 = self._new_tab(
            title=u'Сведения о коррекционных учреждениях')

        self._add_field_set(self.tab_main11,
            u'Информация о педагогическом составе',
            ExtDisplayField(value=(u'Информация о педагогическом составе ' +
                u'специального (коррекционного) учреждения для обучающихся, ' +
                u'воспитанников с ограниченными возможностями здоровья')),
            ExtTextArea(label=u'Информация',
                name='teaching_staff_ci_info', anchor='100%',),
            self._new_visibility_checkbox('teaching_staff_ci_vop')
        )

        self._add_field_set(self.tab_main11,
            u'Категория детей',
            ExtDisplayField(value=(u'Категория детей, имеющих право на ' +
                u'обучение в специальных (коррекционных) учреждениях для ' +
                u'обучающихся, воспитанников с ограниченными ' +
                u'возможностями здоровья')),
            ExtTextArea(label=u'Информация',
                name='category_children_ci_info', anchor='100%',),
            self._new_visibility_checkbox('category_children_ci_vop')
        )

        self._add_field_set(self.tab_main11,
            u'Информация о наличии свободных мест',
            ExtDisplayField(value=(u'Информация о наличии свободных мест в ' +
                u'специальных (коррекционных) группах, классах')),
            ExtTextArea(label=u'Информация',
                name='availability_ci_info', anchor='100%',),
            self._new_visibility_checkbox('availability_ci_vop')
        )

        self.tabs.tabs.extend([
            self.tab_main0, self.tab_main1, self.tab_main2,
            self.tab_main3, self.tab_main4, self.tab_main5,
            self.tab_main6, self.tab_main7, self.tab_main8,
            self.tab_main9, self.tab_main10, self.tab_main11,
        ])

        self.top_panel = ExtPanel(layout='form', region='north',
            height=90, body_cls='x-window-mc')

        self.top_panel.items.extend([
            id,
            self.name_field,
            self.foto,
            self.director,
        ])

        self.form.items.extend([
            self.top_panel,
            self.tabs_panel,
        ])

        self.save_btn = ExtButton(
            text=u'Сохранить', handler='notDismissedWindow')
        self.save_close_btn = ExtButton(
            text=u'Сохранить и закрыть', handler='notDismissedWindow')
        self.cancel_btn = ExtButton(text=u'Отмена', handler='cancelForm')

        self.buttons.extend([
            self.save_btn,
            self.save_close_btn,
            self.cancel_btn
        ])

    def _new_tab(self, title, layout='form'):
        return ExtPanel(title=title, layout=layout,
            #label_width='110',
            body_cls='x-window-mc')

    def _add_field_set(self, panel, title_field_set, *components):
        """
        Добавляет Field Set с наименованием @title на @panel, и добавляет
        компоненты @components
        """
        assert isinstance(panel, ExtPanel)

        fs = ExtFieldSet(title=title_field_set, collapsible=True, anchor='100%')
        fs.items.extend(components)
        for cmp in components:
            if cmp.name:
                setattr(self, cmp.name, cmp)
        panel.items.append(fs)
        return fs


