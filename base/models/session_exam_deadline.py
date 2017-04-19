##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from django.db import models
from django.contrib import admin
from base.models.enums import number_session


class SessionExamDeadlineAdmin(admin.ModelAdmin):
    list_display = ('offer_enrollment', 'deadline', 'deadline_tutor', 'number_session', 'changed')
    list_filter = ('number_session',)
    raw_id_fields = ('offer_enrollment',)
    search_fields = ['offer_enrollment__student__person__first_name','offer_enrollment__student__person__last_name',
                     'number_session']


class SessionExamDeadline(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    deadline = models.DateField()
    deadline_tutor = models.IntegerField(null=True, blank=True)  # Delta day(s)
    number_session = models.IntegerField(choices=number_session.NUMBERS_SESSION)
    offer_enrollment = models.ForeignKey('OfferEnrollment')

    @property
    def deadline_tutor_computed(self):
        if self.deadline_tutor is not None:
            return self.deadline - datetime.timedelta(days=self.deadline_tutor)
        return None

    @property
    def is_deadline_reached(self):
        return self.deadline < datetime.date.today()

    @property
    def is_deadline_tutor_reached(self):
        if self.deadline_tutor_computed:
            return self.deadline_tutor_computed < datetime.date.today()
        return self.is_deadline_reached

    def __str__(self):
        return u"%s-%s" % (self.offer_enrollment, self.number_session)


def filter_by_nb_session(nb_session):
    return SessionExamDeadline.objects.filter(number_session=nb_session)


def get_by_offer_enrollment_nb_session(offer_enrollment, nb_session):
    try:
        return SessionExamDeadline.objects.get(offer_enrollment=offer_enrollment.id,
                                               number_session=nb_session)
    except SessionExamDeadline.DoesNotExist:
        return None