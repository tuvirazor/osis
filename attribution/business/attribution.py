##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from attribution import models as mdl_attr
from base.business.entity_version import find_entity_version_according_academic_year


def get_attributions_list(attributions, responsibles_order):
    dict_attribution = dict()
    for attribution in attributions:
        tutors = mdl_attr.attribution.find_all_tutors_by_learning_unit_year(attribution.learning_unit_year,
                                                                            responsibles_order)
        entity_v = _get_entity_version(attribution.learning_unit_year.learning_container_year)
        dict_attribution[attribution] = [attribution.learning_unit_year.id,
                                         entity_v.acronym,
                                         attribution.learning_unit_year.acronym,
                                         attribution.learning_unit_year.complete_title,
                                         tutors]
    return dict_attribution


def _get_entity_version(learning_container_year_prefetched):
    if learning_container_year_prefetched.entities_containers_year:
        entity = learning_container_year_prefetched.entities_containers_year[0].entity
        if entity.entity_versions:
            return find_entity_version_according_academic_year(entity.entity_versions,
                                                               learning_container_year_prefetched.academic_year)
    return None


def _set_summary_responsible_to_true(attributions):
    for a_attribution in attributions:
        a_attribution.summary_responsible = True
        a_attribution.save()
