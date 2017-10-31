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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from django.utils import timezone
from attribution.models import attribution
from base.models import learning_unit_year
from base.models.enums.learning_unit_year_subtypes import PARTIM, FULL
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory


def create_learning_unit_year(acronym, title, academic_year):
    learning_unit = LearningUnitFactory(acronym=acronym, title=title, start_year=2010)
    return LearningUnitYearFactory(acronym=acronym,
                                   title=title,
                                   academic_year=academic_year,
                                   learning_unit=learning_unit)


class LearningUnitYearTest(TestCase):
    def setUp(self):
        self.tutor = TutorFactory()
        self.academic_year = AcademicYearFactory(year=timezone.now().year)
        self.learning_unit_year = LearningUnitYearFactory(acronym="LDROI1004", title="Juridic law courses",
                                                          academic_year=self.academic_year)

    def test_find_by_tutor_with_none_argument(self):
        self.assertEquals(attribution.find_by_tutor(None), None)

    def test_subdivision_computation(self):
        l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year= l_container_year,
                                           academic_year=self.academic_year)
        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year= l_container_year,
                                           academic_year=self.academic_year)
        l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year= l_container_year,
                                           academic_year=self.academic_year)

        self.assertFalse(l_unit_1.subdivision)
        self.assertEqual(l_unit_2.subdivision, 'A')
        self.assertEqual(l_unit_3.subdivision, 'B')

    def test_search_acronym_by_regex(self):
        regex_valid='^LD.+1+'
        query_result_valid=learning_unit_year.search(acronym=regex_valid)
        self.assertEqual(len(query_result_valid), 1)
        self.assertEqual(self.learning_unit_year.acronym, query_result_valid[0].acronym)

    def test_is_deletable(self):
        l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=FULL)
        msg = []
        self.assertTrue(l_unit_1.is_deletable(msg))
        self.assertEqual(msg, [])

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=PARTIM)
        l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=PARTIM)

        l_enrollement_1 = LearningUnitEnrollmentFactory(learning_unit_year=l_unit_1)
        l_enrollement_2 = LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        self.assertFalse(l_unit_1.is_deletable(msg))
        print(msg)

        msg = []
        component = LearningComponentYearFactory(learning_container_year=l_container_year)
        LearningClassYearFactory(learning_component_year=component)

        self.assertFalse(l_unit_1.is_deletable(msg))
        print(msg)