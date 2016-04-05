#coding:utf-8
"""
Created on Jun 15, 2011

@author: danil
"""
from django.core.cache import cache

from m3_legacy.datagrouping import RecordProxy, GroupingRecordDataProvider
from m3_ext.ui.containers.grids import ExtGridColumn

from web_edu.olap.forms import OlapWindow
from web_edu.core.helpers import get_current_school, get_current_period, \
    filter_self_by_school
from web_edu.core.school.models import School
from web_edu.core.classyear.models import ClassYear
from django.db.models.aggregates import Count
from web_edu.core.daycare.models import DayCare
from web_edu.core.schedule_calls.models import StudyTime

from helpers import replace_space_if_string

class SchoolProxy(RecordProxy):
    raion = None
    school = None
    school_type = None
    def load(self, record):
        EXCLUDED = ('index', 'lindex', 'indent', 'is_leaf', 'expanded', 'count')
        for a in dir(record):
            if (
                not a.startswith('_')
                and not callable(getattr(record, a))
                and a not in  EXCLUDED
                ):

                setattr(self, a, getattr(record, a))
    def calc(self):
        if not self.school_type:
            for code, name in SchoolProvider.territory.values():
                setattr(self, '%s' % code, None)
                setattr(self, '%s_branch' % code, None)

class SchoolProvider(GroupingRecordDataProvider):
    request = None
    proxy_class = SchoolProxy
    aggregates = {}
    types = [
        ('01', u'01.Всего учреждений (сумма строк 02, 03, 11 - 16)'),
        ('02', u'02.образовательные учреждения для детей дошкольного и младшего школьного возраста'),
        ('03', u'03.общеобразовательные учреждения и школы-интернаты (сумма строк 04, 05, 06, 08, 09, 10)'),
        ('04', u'04.начальные'),
        ('05', u'05.основные'),
        ('06', u'06.средние'),
        ('07', u'07.из них (из стр.06) имеющие только 10-11(12) классы'),
        ('08', u'08.общеобразовательные учреждения с углубленным изучением отдельных предметов'),
        ('09', u'09.гимназии'),
        ('10', u'10.лицеи'),
        ('11', u'11.кадетские учреждения'),
        ('12', u'12.общеобразовательные школы-интернаты с первоначальной летной подготовкой'),
        ('13', u'13.специальные (коррекционные) образовательные учреждения для обучающихся, воспитанников с ограниченными возможностями здоровья'),
        ('14', u'14.специальные учебно-воспитательные учреждения для детей и подростков с девиантным поведением'),
        ('15', u'15.оздоровительные образовательные учреждения санаторного типа для детей, нуждающихся в длительном лечении'),
        ('16', u'16.образовательные учреждения для детей, нуждающихся в психолого-педагогической и медико-социальной помощи'),
        ('17', u'17.Из них( из стр.01):образовательные учреждения для детей-сирот и детей, оставшихся без попечения родителей'),
        ('18', u'18.учреждения с группами продленного  дня'),
        ('19', u'19.учреждения, ведущие занятия:в две смены'),
        ('20', u'20.в три смены'),
        ]
    territory = {
        1: ('city', u'01.Городские поселения'),
        2: ('ferm', u'02.Сельская местность'),
        99: ('total', u'03.Итого'),
        }

    def get_types(self, institution_type, institution_variant, school, dicts):
        """
        вернет лист типов учреждений для которых подходит эта школа
        institution_type - тип
        institution_variant - вид
        """
        res = []
        if institution_type == u'Дошкольное образовательное учреждение':
            res.append('02')
        if institution_variant in [
            u'Школа - интернат начального общего образования',
            u'Начальная общеобразовательная школа',
           ]:
            res.append('04')
        if institution_variant in [
            u'Основная общеобразовательная школа',
            u'Школа - интернат основного общего образования',
           ]:
            res.append('05')
        if institution_variant in [
            u'Средняя (полная) общеобразовательная школа',
            u'Средняя (полная) общеобразовательная школа, в т.ч. с углубленным изучением отдельных предметов'
            u'Школа - интернат среднего (полного) общего образования, в т.ч. с углубленным изучением отдельных предметов',
           ]:
            res.append('06')
        if '06' in res and school in dicts['only1012classes']:
            res.append('07')
        if institution_variant in [
            u'Средняя (полная) общеобразовательная школа, в т.ч. с углубленным изучением отдельных предметов'
            u'Школа - интернат среднего (полного) общего образования, в т.ч. с углубленным изучением отдельных предметов',
           ]:
            res.append('08')
        if institution_variant in [
            u'Гимназия'
            u'Гимназия - интернат',
           ]:
            res.append('09')
        if institution_variant in [
            u'Лицей'
            u'Лицей - интернат',
           ]:
            res.append('10')
        if institution_variant in [
            u'Кадетская школа'
            u'Кадетская школа – интернат',
           ]:
            res.append('11')
        if institution_variant in [
            u'Школа – интернат с первоначальной летной подготовкой',
           ]:
            res.append('12')
        if institution_type in [
            u'Специальное (коррекционное) образовательное учреждение для обучающихся воспитанников с отклонениями в развитии',
           ]:
            res.append('13')
        if institution_type in [
            u'Специальное учебно-воспитательное учреждение открытого и закрытого типа (для детей с девиантным поведением)',
           ]:
            res.append('14')
        if institution_type in [
            u'TODO: оздоровительные образовательные учреждения санаторного типа для детей, нуждающихся в длительном лечении',
           ]:
            res.append('15')
        if institution_type in [
            u'TODO: вательные учреждения для детей, нуждающихся в психолого-педагогической и медико-социальной помощи',
           ]:
            res.append('16')
        if institution_type in [
            u'Образовательное учреждение для детей-сирот и детей, оставшихся без попечения родителей',
           ]:
            res.append('17')
        if school in dicts['daycare']:
            res.append('18')
        if school in dicts['2smen']:
            res.append('19')
        if school in dicts['3smen']:
            res.append('20')
        for f in ('04', '05', '06', '08', '09', '10'):
            if f in res:
                res.append('03')
                break
        for f in ('02', '03', '11', '12', '13', '14', '15', '16'):
            if f in res:
                res.append('01')
                break
        return res



    def __init__(self, request, *args, **kwargs):
        self.request = request
        for code, name in self.territory.values():
            self.aggregates['%s' % code] = 'sum'
            self.aggregates['%s_branch' % code] = 'sum'

        super(SchoolProvider, self).__init__(*args, **kwargs)

        key = self.get_key(*args, **kwargs)
        data = cache.get(key)
        if not data:
            data = self.create_data(*args, **kwargs)
            cache.set(key, data, 10 * 60)

        self.data_source = data

    @replace_space_if_string
    def get_key(self, *args, **kwargs):
        """
        ключ для кэширования
        """
        school = get_current_school(self.request)
        period = get_current_period(self.request)
        return 'SchoolProvider_%s%s' % (school, period)

    def get_type_by_code(self, code):
        for c, name in self.types:
            if c == code:
                return name

    def create_data(self, *args, **kwargs):
        """
        заполним лист с данными
        """
        data = []
        q = School.objects.select_related('institution_type', 'institution_variant', 'parent')
        q = q.filter(parent__isnull=False)
        q = q.filter(filter_self_by_school(get_current_school(self.request)))
        dicts = {}
        dicts['only1012classes'] = self.get_only1012classes()
        dicts['daycare'] = self.get_daycare()
        dicts['2smen'], dicts['3smen'] = self.get_23smen()

        for school in q:
            own_types = self.get_types(
                    getattr(school.institution_type, 'name', 'None'),
                    getattr(school.institution_variant, 'name', 'None'),
                    school.id, dicts)
            for type, type_name in self.types:
                obj = SchoolProxy()
                obj.school = school.name
                obj.raion = school.parent.name
                obj.school_type = type_name
                for code, name in self.territory.values():
                    setattr(obj, '%s_branch' % code, 0)
                    setattr(obj, '%s' % code, 0)

                if type in own_types:
                    ter_code, stub = self.territory.get(school.territory_type, ('city', None))
                    for code in (ter_code, 'total'):
                        if school.branch:
                            setattr(obj, '%s_branch' % code, 1)
                        else:
                            setattr(obj, '%s' % code, 1)
                data.append(obj)
        return data

    def get_only1012classes(self):
        """
        школы где только 10-12 классы
        """
        q = ClassYear.objects
        q = q.filter(period=get_current_period(self.request))
        q = q.values('school')
        q = q.annotate(cnt=Count('id'))
        c19 = {}
        for obj in q.filter(study_level__index__lte=9).iterator():
            c19[obj['school']] = True
        res = {}
        for obj in q.filter(study_level__index__gte=10).iterator():
            if obj['school'] not in c19:
                res[obj['school']] = True
        return res

    def get_daycare(self):
        """
        школы где продленка и сгущенка
        """
        q = DayCare.objects
        q = q.filter(period=get_current_period(self.request))
        q = q.values('school')
        q = q.annotate(cnt=Count('id'))
        res = {}
        for obj in q.iterator():
            res[obj['school']] = True
        return res

    def get_23smen(self):
        """
        школы где 2,3 смены
        """
        q = StudyTime.objects
        q = q.values('school')
        q = q.annotate(cnt=Count('id'))
        res2 = {}
        res3 = {}

        for obj in q.iterator():
            if obj['cnt'] == 2:
                res2[obj['school']] = True
            if obj['cnt'] == 3:
                res3[obj['school']] = True

        return res2, res3


class SchoolOLAPWindow(OlapWindow):
    def __init__(self, *args, **kwargs):
        super(SchoolOLAPWindow, self).__init__(*args, **kwargs)

        self.grid.columns.append(ExtGridColumn(header=u'ИД', data_index='id', hidden=True))
        self.grid.columns.append(ExtGridColumn(
            header=u'Район',
            data_index='raion',
            extra={'groupable': True, 'summaryType': '"count"'},
            sortable=True
        ))
        self.grid.columns.append(ExtGridColumn(
            header=u'Учреждение',
            data_index='school',
            extra={'groupable': True, 'summaryType': '"count"'},
            sortable=True
        ))
        self.grid.columns.append(ExtGridColumn(
            header=u'Тип',
            data_index='school_type',
            extra={'groupable': True, 'summaryType': '"count"'},
            sortable=True
        ))

        self.grid.add_banded_column(None, 1, 5)
        for br, br_name in (('', u'01.Число учреждений'), ('_branch', u'02.кроме того, филиалов')):
            for code, name in SchoolProvider.territory.values():
                self.grid.columns.append(ExtGridColumn(
                    header=name,
                    data_index='%s%s' % (code, br),
                    extra={'groupable': False, 'summaryType': '"sum"'},
                    sortable=True,
                ))
            self.grid.add_banded_column(ExtGridColumn(header=br_name, align='center'), 1, 3)


        self.grid.grouped = ['raion', 'school', 'school_type']

