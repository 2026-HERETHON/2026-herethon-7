from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Proposal
from project.models import Project, ProjectMember


@transaction.atomic
def accept_proposal(proposal):
    """
    협업 제안 수락

    - 제안 상태 변경
    - 프로젝트 생성
    - 프로젝트 멤버 생성
    """

    proposal.status = Proposal.Status.ACCEPT
    proposal.save(update_fields=["status"])

    start_date = timezone.now().date()

    end_date = start_date + timedelta(
        weeks=proposal.period
    )

    project = Project.objects.create(
        proposal=proposal,
        title=proposal.title,
        progress=0,
        status=Project.Status.IN_PROGRESS,
        start_date=start_date,
        end_date=end_date,
    )

    ProjectMember.objects.bulk_create([
        ProjectMember(
            project=project,
            user=proposal.sender,
            role=proposal.give_talent.name,
        ),
        ProjectMember(
            project=project,
            user=proposal.receiver,
            role=proposal.need_talent.name,
        ),
    ])

    return project