#coding:utf-8
"""
Базовые модели для заполнения данных учреждения.

Created on 11.11.2010

@author: prefer
"""


from django.conf import settings
from django.db import models
from web_edu.m3_backports import mie
from web_edu.core.teacher.models import Teacher
from web_edu.core.school.models import School
from web_edu.core.models import LoggingQuerySetManager, BaseReplicatedModel
from web_edu.core.helpers import upload_file_handler
from web_edu.core.secure_media.fields import DescFileField


def content_file_name(instance, filename):
    return '/'.join([settings.DOWNLOADS, filename])


class BaseEmieModel(mie.SimpleModelExtender, BaseReplicatedModel):
    """
    Базовая модель для Данных учреждения
    Постфикс _vop у полей озночает visible on portal,
    то есть будут ли отображаться
    такие поля на портале
    """
    objects = LoggingQuerySetManager()

    school = models.OneToOneField(School, related_name='ext_school')
    director = models.ForeignKey(Teacher, null=True, blank=True,
                                 db_index=True, on_delete=models.SET_NULL)
    foto = models.FileField(
        upload_to=upload_file_handler, null=True, blank=True, max_length=255)

    # Контактная информация
    web_site = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    # Устав
    ustav_file =DescFileField(upload_to=upload_file_handler, max_length=255)
    ustav_vop = models.BooleanField(default=False)

    #Лицензия и аккредитация
    license_info = models.TextField(null=True, blank=True)
    license_file = models.FileField(upload_to=upload_file_handler, max_length=255)
    license_vop = models.BooleanField(default=False)

    akkred_info = models.TextField(null=True, blank=True)
    akkred_file = models.FileField(upload_to=upload_file_handler, max_length=255)
    akkred_vop = models.BooleanField(default=False)

    # Язык обучения
    language_info = models.TextField(null=True, blank=True)
    language_vop = models.BooleanField(default=False)

    # Планируемые показатели приема
    projected_rates_info = models.TextField(null=True, blank=True)
    projected_rates_vop = models.BooleanField(default=False)

    # Зачисление в ОУ
    enrollment_docs_in_ou_info = models.TextField(null=True, blank=True)
    enrollment_docs_in_ou_file = DescFileField(
        upload_to=upload_file_handler, max_length=255)
    enrollment_docs_in_ou_vop = models.BooleanField(default=False)

    # Продолжительность обучения
    durations_info = models.TextField(null=True, blank=True)
    durations_vop = models.BooleanField(default=False)

    mode_employment_info = models.TextField(null=True, blank=True)
    mode_employment_vop = models.BooleanField(default=False)

    # Отчисление
    deduction_info = models.TextField(null=True, blank=True)
    deduction_vop = models.BooleanField(default=False)

    # Доп. услуги
    additional_services_info = models.TextField(null=True, blank=True)
    additional_services_vop = models.BooleanField(default=False)

    # Количество групп санаторного типа
    sanator_groups = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True
