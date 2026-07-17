from django.db import transaction

from user.models import Portfolio
from .models import Project, ProjectMember, Task


@transaction.atomic
def update_task_status(task, status):
    """
    업무 상태 변경

    - 진행률 계산
    - 프로젝트 완료 여부 갱신
    - 완료 시 포트폴리오 자동 생성
    """

    task.status = status
    task.save(update_fields=["status"])

    project = task.project

    total_count = Task.objects.filter(
        project=project
    ).count()

    done_count = Task.objects.filter(
        project=project,
        status=Task.Status.DONE,
    ).count()

    if total_count == 0:
        progress = 0
    else:
        progress = int(done_count / total_count * 100)

    project.progress = progress

    if total_count > 0 and done_count == total_count:

        project.status = Project.Status.COMPLETED

        members = ProjectMember.objects.filter(project=project)

        for member in members:
            Portfolio.objects.get_or_create(
                project=project,
                user=member.user,
                defaults={
                    "title": project.title,
                    "role": member.role,
                    "summary": project.proposal.goal,
                },
            )
    else:

        project.status = Project.Status.IN_PROGRESS

    project.save(
        update_fields=[
            "progress",
            "status",
        ]
    )

    return project
