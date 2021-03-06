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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages import ERROR
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from base.business import learning_unit_proposal as business_proposal
from base.business.learning_units import perms
from base.models.enums import proposal_type, proposal_state
from base.models.person import Person
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.views.common import display_error_messages, display_most_critical_messages


@login_required
@require_POST
@permission_required('base.can_consolidate_learningunit_proposal', raise_exception=True)
def consolidate_proposal(request):
    learning_unit_year_id = request.POST.get("learning_unit_year_id")
    proposal = get_object_or_404(ProposalLearningUnit, learning_unit_year__id=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)

    if not perms.is_proposal_in_state_to_be_consolidated(proposal):
        raise PermissionDenied("Proposal learning unit is neither accepted nor refused.")

    result = {}
    try:
        result = business_proposal.consolidate_proposal(proposal, author=user_person, send_mail=True)
        display_most_critical_messages(request, result)
    except IntegrityError as e:
        display_error_messages(request, e.args[0])

    return _consolidate_proposal_redirection(proposal, result)


def _consolidate_proposal_redirection(proposal, consolidation_result):
    if proposal.type == proposal_type.ProposalType.CREATION.name and \
            proposal.state == proposal_state.ProposalState.REFUSED.name and not consolidation_result.get(ERROR, []):
        return redirect('learning_units')
    return redirect('learning_unit', learning_unit_year_id=proposal.learning_unit_year.id)
