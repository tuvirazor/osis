##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db import models


class InternshipStudentAffectationStat(models.Model):
    student = models.ForeignKey('base.Student')
    organization = models.ForeignKey('internship.Organization')
    speciality = models.ForeignKey('internship.InternshipSpeciality')
    period = models.ForeignKey('internship.Period')
    choice = models.CharField(max_length=1, blank=False, null=False, default='0')
    cost = models.IntegerField(blank=False, null=False)
    consecutive_month = models.BooleanField(default=False, null=False)
    type_of_internship = models.CharField(max_length=1, blank=False, null=False, default='N')

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipStudentAffectationStat.objects.filter(**kwargs)\
            .select_related("student__person", "organization", "speciality", "period")\
            .order_by("student__person__last_name","student__person__first_name", "period__date_start")
        return queryset

    @staticmethod
    def find_by_id(affectation_id):
        return InternshipStudentAffectationStat.objects.get(pk=affectation_id)
