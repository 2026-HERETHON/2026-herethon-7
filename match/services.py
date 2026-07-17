from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Proposal
from project.models import Project, ProjectMember
from user.models import ProfileTalent


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

def calculate_match_percent(user_a, user_b):
    """매칭 퍼센트 계산"""
    profile_a = getattr(user_a, 'profile', None)
    profile_b = getattr(user_b, 'profile', None)

    if not profile_a or not profile_b:
        return 0

    a_give = set(
        ProfileTalent.objects.filter(
            profile=profile_a, type='GIVE'
        ).values_list('talent_id', flat=True)
    )
    a_need = set(
        ProfileTalent.objects.filter(
            profile=profile_a, type='NEED'
        ).values_list('talent_id', flat=True)
    )
    b_give = set(
        ProfileTalent.objects.filter(
            profile=profile_b, type='GIVE'
        ).values_list('talent_id', flat=True)
    )
    b_need = set(
        ProfileTalent.objects.filter(
            profile=profile_b, type='NEED'
        ).values_list('talent_id', flat=True)
    )

    matched = len(a_give & b_need) + len(b_give & a_need)
    total_need = len(a_need) + len(b_need)

    if total_need == 0:
        return 0

    return round((matched / total_need) * 100)