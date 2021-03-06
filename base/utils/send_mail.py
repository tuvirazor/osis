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

"""
Utility files for mail sending
"""

from django.utils.translation import ugettext as _
from assessments.business import score_encoding_sheet

from osis_common.models import message_history as message_history_mdl
from osis_common.messaging import message_config, send_message as message_service
from base.models import person as person_mdl
from osis_common.document import paper_sheet

EDUCATIONAL_INFORMATION_UPDATE_TXT = 'educational_information_update_txt'

EDUCATIONAL_INFORMATION_UPDATE_HTML = 'educational_information_update_html'


def send_mail_after_scores_submission(persons, learning_unit_name, submitted_enrollments, all_encoded):
    """
    Send an email to all the teachers after the scores submission for a learning unit
    :param persons: The list of the teachers of the leaning unit
    :param learning_unit_name: The name of the learning unit for which scores were submitted
    :param submitted_enrollments : The list of newly sibmitted enrollments
    :param all_encoded : Tell if all the scores are encoded and submitted
    :return An error message if the template is not in the database
    """

    html_template_ref = 'assessments_scores_submission_html'
    txt_template_ref = 'assessments_scores_submission_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language) for person in persons]
    suject_data = {'learning_unit_name': learning_unit_name}
    template_base_data = {'learning_unit_name': learning_unit_name,
                          'encoding_status':    _('encoding_status_ended') if all_encoded
                          else _('encoding_status_notended')
                          }
    header_txt = ['acronym', 'session_title', 'registration_number', 'lastname', 'firstname', 'score', 'documentation']
    submitted_enrollments_data = [
        (
            enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            enrollment.session_exam.number_session,
            enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            enrollment.score_final,
            _(enrollment.justification_final) if enrollment.justification_final else None,
        ) for enrollment in submitted_enrollments]
    table = message_config.create_table('submitted_enrollments', header_txt, submitted_enrollments_data)

    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, [table], receivers,
                                                            template_base_data, suject_data)
    return message_service.send_messages(message_content)


def send_mail_after_the_learning_unit_year_deletion(managers, acronym, academic_year, msg_list):
    html_template_ref = 'learning_unit_year_deletion_html'
    txt_template_ref = 'learning_unit_year_deletion_txt'
    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language) for manager in managers]
    suject_data = {'learning_unit_acronym': acronym}
    template_base_data = {'learning_unit_acronym': acronym,
                          'academic_year': academic_year,
                          'msg_list':msg_list,
                          }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, suject_data, None)
    return message_service.send_messages(message_content)


def send_mail_after_the_learning_unit_proposal_cancellation(managers, proposals):
    html_template_ref = 'learning_unit_proposal_canceled_html'
    txt_template_ref = 'learning_unit_proposal_canceled_txt'
    return _send_mail_after_learning_unit_proposal_action(managers, proposals, html_template_ref, txt_template_ref)


def send_mail_after_the_learning_unit_proposal_consolidation(managers, proposals):
    html_template_ref = 'learning_unit_proposal_consolidated_html'
    txt_template_ref = 'learning_unit_proposal_consolidated_txt'
    return _send_mail_after_learning_unit_proposal_action(managers, proposals, html_template_ref, txt_template_ref)


def _send_mail_after_learning_unit_proposal_action(managers, proposals, html_template_ref, txt_template_ref):
    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language) for manager in managers]
    suject_data = {}
    template_base_data = {'proposals': proposals}
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, suject_data, None)
    return message_service.send_messages(message_content)


def send_message_after_all_encoded_by_manager(persons, enrollments, learning_unit_acronym, offer_acronym):
    """
    Send a message to all tutor from a learning unit when all scores are submitted by program manager
    :param persons: The list of the tutor (person) of the learning unit
    :param enrollments: The enrollments that are encoded and submitted
    :param learning_unit_acronym The learning unit encoded
    :param offer_acronym: The offer which is managed
    :return: A message if an error occured, None if it's ok
    """

    html_template_ref = 'assessments_all_scores_by_pgm_manager_html'
    txt_template_ref = 'assessments_all_scores_by_pgm_manager_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language) for person in persons]
    suject_data = {
        'learning_unit_acronym': learning_unit_acronym,
        'offer_acronym':         offer_acronym
    }
    template_base_data = {
        'learning_unit_acronym':    learning_unit_acronym,
        'offer_acronym':            offer_acronym,
    }
    enrollments_data = [
        (
            enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            enrollment.session_exam.number_session,
            enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            enrollment.score_final,
            _(enrollment.justification_final) if enrollment.justification_final else None,
        ) for enrollment in enrollments]
    enrollments_headers = (
        'acronym',
        'session_title',
        'registration_number',
        'lastname',
        'firstname',
        'score',
        'documentation'
    )
    table = message_config.create_table('enrollments', enrollments_headers, enrollments_data)
    attachment = build_scores_sheet_attachment(enrollments)
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            [table], receivers, template_base_data, suject_data,
                                                            attachment)
    return message_service.send_messages(message_content)


def build_scores_sheet_attachment(list_exam_enrollments):
    name = "%s.pdf" % _('scores_sheet')
    mimetype = "application/pdf"
    content = paper_sheet.build_pdf(
        score_encoding_sheet.scores_sheet_data(list_exam_enrollments, tutor=None))
    return (name, content, mimetype)


def send_again(message_history_id):
    """
    send a message from message history again
    :param message_history_id The id of the message history to send again
    :return the sent message

    TO-DO : correction of send_message in osis-common to get the associated receiver , based on id and receiver model

    """
    message_history = message_history_mdl.find_by_id(message_history_id)
    person = person_mdl.find_by_id(message_history.receiver_id)
    if person:
        receiver = message_config.create_receiver(person.id, person.email, person.language)
        return message_service.send_again(receiver, message_history_id)
    else:
        return _('no_receiver_error')


def send_mail_for_educational_information_update(teachers, learning_units_years):
    html_template_ref = EDUCATIONAL_INFORMATION_UPDATE_HTML
    txt_template_ref = EDUCATIONAL_INFORMATION_UPDATE_TXT
    receivers = [message_config.create_receiver(teacher.id, teacher.email, teacher.language) for teacher in teachers]
    template_base_data = {'learning_unit_years': learning_units_years}

    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, {}, None)
    return message_service.send_messages(message_content)
