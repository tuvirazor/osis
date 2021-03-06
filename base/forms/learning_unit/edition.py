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
from django import forms
from django.core.exceptions import ValidationError
from django.forms import model_to_dict
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit import compute_max_academic_year_adjournment
from base.business.learning_units.edition import filter_biennial, update_learning_unit_year_with_report, \
    edit_learning_unit_end_date
from base.business.learning_units.perms import FACULTY_UPDATABLE_CONTAINER_TYPES
from base.forms.learning_unit_create import LearningUnitYearForm, PARTIM_FORM_READ_ONLY_FIELD
from base.forms.utils.choice_field import add_blank
from base.models import academic_year, entity_container_year
from base.models import learning_unit_year
from base.models.academic_year import AcademicYear
from base.models.enums.attribution_procedure import AttributionProcedures
from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.learning_container_year_types import INTERNSHIP, \
    LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES
from base.models.enums.learning_unit_periodicity import ANNUAL
from base.models.enums.learning_unit_year_subtypes import PARTIM
from base.models.enums.vacant_declaration_type import VacantDeclarationType

FULL_READ_ONLY_FIELDS = {"first_letter", "acronym", "academic_year", "container_type", "subtype"}
PARTIM_READ_ONLY_FIELDS = PARTIM_FORM_READ_ONLY_FIELD | {"is_vacant", "team", "type_declaration_vacant",
                                                         "attribution_procedure", "subtype"}
FACULTY_READ_ONLY_FIELDS = {"periodicity", "common_title", "common_title_english", "specific_title",
                            "specific_title_english", "campus", "status", "credits", "language",
                            "requirement_entity", "allocation_entity", "additional_requirement_entity_2", "is_vacant",
                            "type_declaration_vacant", "attribution_procedure", "subtype"}


# TODO Convert it in ModelForm
class LearningUnitEndDateForm(forms.Form):
    academic_year = forms.ModelChoiceField(required=False,
                                           queryset=AcademicYear.objects.none(),
                                           empty_label=_('not_end_year'),
                                           label=_('academic_end_year')
                                           )

    def __init__(self, data, learning_unit, *args, max_year=None, **kwargs):
        self.learning_unit = learning_unit
        super().__init__(data, *args, **kwargs)
        end_year = self.learning_unit.end_year

        self._set_initial_value(end_year)

        try:
            queryset = self._get_academic_years(max_year)

            periodicity = self.learning_unit.periodicity
            self.fields['academic_year'].queryset = filter_biennial(queryset, periodicity)
        except ValueError:
            self.fields['academic_year'].disabled = True

        if max_year:
            self.fields['academic_year'].required = True

    def _set_initial_value(self, end_year):
        try:
            self.fields['academic_year'].initial = AcademicYear.objects.get(year=end_year)
        except (AcademicYear.DoesNotExist, AcademicYear.MultipleObjectsReturned):
            self.fields['academic_year'].initial = None

    def _get_academic_years(self, max_year):
        current_academic_year = academic_year.current_academic_year()
        min_year = current_academic_year.year

        if not max_year:
            max_year = compute_max_academic_year_adjournment()

        if self.learning_unit.start_year > min_year:
            min_year = self.learning_unit.start_year

        if self.learning_unit.is_past():
            raise ValueError(
                'Learning_unit.end_year {} cannot be less than the current academic_year {}'.format(
                    self.learning_unit.end_year, current_academic_year)
            )

        if min_year > max_year:
            raise ValueError('Learning_unit {} cannot be modify'.format(self.learning_unit))

        return academic_year.find_academic_years(start_year=min_year, end_year=max_year)

    def save(self, update_learning_unit_year=True):
        return edit_learning_unit_end_date(self.learning_unit, self.cleaned_data['academic_year'],
                                           update_learning_unit_year)


def _create_type_declaration_vacant_list():
    return add_blank(VacantDeclarationType.translation_choices())


def _create_attribution_procedure_list():
    return add_blank(AttributionProcedures.translation_choices())


class LearningUnitModificationForm(LearningUnitYearForm):
    is_vacant = forms.BooleanField(required=False)
    team = forms.BooleanField(required=False)
    type_declaration_vacant = forms.ChoiceField(required=False, choices=_create_type_declaration_vacant_list())
    attribution_procedure = forms.ChoiceField(required=False, choices=_create_attribution_procedure_list())

    learning_unit_year_subtype = None
    learning_container_type = None
    parent = None

    def __init__(self, *args, person, learning_unit_year_instance, **kwargs):
        self.instance = learning_unit_year_instance
        self.learning_unit_end_date = kwargs.pop("end_date", None)

        super().__init__(*args, initial=compute_form_initial_data(self.instance), **kwargs)
        self.postponement = bool(int(self.data.get('postponement', 1)))

        if self.initial:
            self.learning_unit_year_subtype = self.initial.get("subtype")
            self.learning_container_type = self.initial.get("container_type")

        self.parent = self.instance.parent

        self.fields["requirement_entity"].queryset = person.find_main_entities_version

        self._disabled_fields_base_on_learning_unit_year_subtype(self.learning_unit_year_subtype)
        self._disabled_internship_subtype_field_if_not_internship_container_type(self.learning_container_type)

        if self.parent:
            self._set_status_value()
            self._enabled_periodicity()

        if person.is_faculty_manager():
            if self.learning_container_type in FACULTY_UPDATABLE_CONTAINER_TYPES and\
                    self.learning_unit_year_subtype == "FULL":
                self._disabled_fields(FACULTY_READ_ONLY_FIELDS)

        if learning_unit_year_instance:
            self.learning_unit = learning_unit_year_instance.learning_unit

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        requirement_entity = cleaned_data["requirement_entity"]
        if not self._is_requirement_entity_end_date_valid(requirement_entity):
            self.add_error("requirement_entity", _("requirement_entity_end_date_too_short"))
        return cleaned_data

    def clean_status(self):
        status = self.cleaned_data['status']
        if self.parent:
            parent_status = self.parent.status
            if not parent_status and parent_status != status:
                raise ValidationError(_('The partim must be inactive because the parent is inactive'))
        elif not status and self.instance.get_partims_related().filter(status=True).count():
            raise ValidationError(_('The parent must be active because there are partim active'))
        return status

    def _is_requirement_entity_end_date_valid(self, requirement_entity):
        if requirement_entity.end_date is None:
            return True
        if self.learning_unit_end_date is None:
            return False
        return requirement_entity.end_date >= self.learning_unit_end_date

    def _disabled_fields_base_on_learning_unit_year_subtype(self, subtype):
        if subtype == PARTIM:
            self._disabled_fields(PARTIM_READ_ONLY_FIELDS)
        else:
            self._disabled_fields(FULL_READ_ONLY_FIELDS)

    def _disabled_internship_subtype_field_if_not_internship_container_type(self, container_type):
        if container_type != INTERNSHIP:
            self._disabled_fields(["internship_subtype"])

    def _disabled_fields(self, fields_to_disable):
        for field in fields_to_disable:
            self.fields[field].disabled = True

    def _set_status_value(self):
        if self.parent.status is False:
            self.fields["status"].initial = self.parent.status
            self.fields["status"].disabled = True

    def _enabled_periodicity(self):
        can_modify_periodicity = self.parent.learning_unit.periodicity == ANNUAL
        self.fields["periodicity"].disabled = not can_modify_periodicity

    def get_data_for_learning_unit(self):
        data_without_entities = {field: value for field, value in self.cleaned_data.items()
                                 if field.upper() not in ENTITY_TYPE_LIST}
        lu_data = {field: value for field, value in data_without_entities.items()
                   if field not in FULL_READ_ONLY_FIELDS}
        return lu_data

    def get_entities_data(self):
        return {entity_type.upper(): entity_version.entity if entity_version else None
                for entity_type, entity_version in self.cleaned_data.items()
                if entity_type.upper() in ENTITY_TYPE_LIST}

    def save(self):
        entities_data = self.get_entities_data()
        lu_type_full_data = self.get_data_for_learning_unit()
        update_learning_unit_year_with_report(self.instance, lu_type_full_data, entities_data,
                                              with_report=self.postponement)


def compute_learning_unit_form_initial_data(learning_unit_year, fields):
    initial_data = {}
    initial_data.update(model_to_dict(learning_unit_year, fields=fields["learning_unit_year"]))
    initial_data.update(model_to_dict(learning_unit_year.learning_container_year,
                                      fields=fields["learning_container_year"]))
    initial_data.update(model_to_dict(learning_unit_year.learning_unit,
                                      fields=fields["learning_unit"]))
    initial_data.update(_get_attributions_of_learning_unit_year(learning_unit_year))
    return {key: value for key, value in initial_data.items() if value is not None}


def _get_attributions_of_learning_unit_year(learning_unit_year):
    attributions = entity_container_year.find_last_entity_version_grouped_by_linktypes(
        learning_unit_year.learning_container_year
    )
    return {k.lower(): v.pk for k, v in attributions.items() if v is not None}


def compute_form_initial_data(learning_unit_year):
    fields = {
        "learning_unit_year": ("academic_year", "status", "credits", "session", "subtype", "quadrimester",
                               "attribution_procedure", "internship_subtype", "specific_title",
                               "specific_title_english", "acronym"),
        "learning_container_year": ("common_title", "common_title_english", "container_type", "campus", "language",
                                    "is_vacant", "team", "type_declaration_vacant"),
        "learning_unit": ("faculty_remark", "other_remark", "periodicity")
    }

    form_data = compute_learning_unit_form_initial_data(learning_unit_year, fields).copy()
    form_data["first_letter"] = form_data["acronym"][0]
    form_data["acronym"] = form_data["acronym"][1:]
    return form_data
