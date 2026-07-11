import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404
from django.views.decorators.http import require_POST
from .models import Project, Task, ProjectFile
from user.models import Portfolio
from .forms import TaskForm, ProjectFileForm

logger = logging.getLogger(__name__)


@login_required
def project_list(request):
    """
    프로젝트 목록

    - 내가 참여 중인 프로젝트 조회
    - 진행중 / 완료 필터 지원
    """

    try:

        # GET 필터
        status = request.GET.get("status")

        # 내가 참여한 프로젝트
        projects = (
            Project.objects.filter(
                projectmember__user=request.user
            )
            .select_related(
                "proposal",
            )
            .distinct()
        )

        # 진행 상태 필터
        if status in [
            Project.Status.IN_PROGRESS,
            Project.Status.COMPLETED,
        ]:

            projects = projects.filter(
                status=status
            )

        context = {

            "projects": projects,
            "selected_status": status,

        }

        return render(
            request,
            "project/project_list.html",
            context,
        )

    except Exception:

        logger.exception("project_list() 오류")

        messages.error(
            request,
            "프로젝트 목록을 불러오는 중 오류가 발생했습니다."
        )

        return render(
            request,
            "project/project_list.html",
            {
                "projects": [],
                "selected_status": None,
            },
        )
    
@login_required
def project_overview(request, project_id):
    """
    프로젝트 워크스페이스 개요

    표시 정보
    - 프로젝트 정보
    - 제안 정보
    - 참여 멤버
    """

    try:

        # 프로젝트 조회 (참여 중인 프로젝트만 접근 가능)
        project = get_object_or_404(

            Project.objects.select_related(
                "proposal"
            ).prefetch_related(
                "projectmember_set__user"
            ),

            pk=project_id,
            projectmember__user=request.user,

        )

        context = {

            "project": project,

            # 템플릿에서 반복문으로 사용
            "members": project.projectmember_set.all(),

        }

        return render(
            request,
            "project/overview.html",
            context,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("project_overview() 오류")

        messages.error(
            request,
            "프로젝트 정보를 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )
    
@login_required
def task_list(request, project_id):
    """
    업무(Task) 목록

    표시 정보
    - 프로젝트 정보
    - 업무 목록
    - 업무 추가 폼
    - 전체 진행률
    """

    try:

        # 프로젝트 조회 (참여자만 접근 가능)
        project = get_object_or_404(
            Project,
            pk=project_id,
            projectmember__user=request.user,
        )

        # 업무 목록
        tasks = (
            Task.objects.filter(
                project=project
            )
            .select_related(
                "assignee"
            )
            .order_by(
                "deadline",
                "created_at",
            )
        )

        # 업무 추가 폼
        form = TaskForm(
            project=project
        )

        progress = project.progress

        context = {

            "project": project,

            "tasks": tasks,

            "form": form,

            "progress": progress,

        }

        return render(
            request,
            "project/tasks.html",
            context,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("task_list() 오류")

        messages.error(
            request,
            "업무 목록을 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )
    


@require_POST
@login_required
def task_create(request, project_id):
    """
    업무 생성

    - 프로젝트 참여자만 생성 가능
    - 담당자는 프로젝트 멤버만 선택 가능
    """

    try:

        project = get_object_or_404(

            Project,

            pk=project_id,
            projectmember__user=request.user,

        )

        form = TaskForm(
            request.POST,
            project=project,
        )

        if form.is_valid():

            task = form.save(commit=False)

            task.project = project

            task.save()

            messages.success(
                request,
                "업무가 추가되었습니다."
            )

        else:

            messages.error(
                request,
                "입력값을 확인해주세요."
            )

        return redirect(
            "project:task_list",
            project_id=project.pk,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("task_create() 오류")

        messages.error(
            request,
            "업무를 추가하는 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )
    
@require_POST
@login_required
def task_update(request, project_id, task_id):
    """
    업무 상태 변경

    - 프로젝트 참여자만 수정 가능
    - 진행률 자동 계산
    - 모든 업무 완료 시 프로젝트 자동 완료
    """

    try:

        # 프로젝트 조회
        project = get_object_or_404(
            Project,
            pk=project_id,
            projectmember__user=request.user,
        )

        # 업무 조회
        task = get_object_or_404(
            Task,
            pk=task_id,
            project=project,
        )

        # 변경할 상태
        status = request.POST.get("status")

        if status not in [
            Task.Status.TODO,
            Task.Status.DOING,
            Task.Status.DONE,
        ]:

            messages.error(
                request,
                "잘못된 업무 상태입니다."
            )

            return redirect(
                "project:task_list",
                project_id=project.pk,
            )

        # -----------------------------
        # 상태 변경
        # -----------------------------
        task.status = status
        task.save(update_fields=["status"])

        # -----------------------------
        # 진행률 계산
        # -----------------------------
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

        # -----------------------------
        # 프로젝트 진행률 저장
        # -----------------------------
        project.progress = progress

        # -----------------------------
        # 프로젝트 완료 여부
        # -----------------------------
        if total_count > 0 and done_count == total_count:

            project.status = Project.Status.COMPLETED

            Portfolio.objects.get_or_create(
                project=project,
                defaults={
                    "title": project.title,
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

        messages.success(
            request,
            "업무 상태가 변경되었습니다."
        )

        return redirect(
            "project:task_list",
            project_id=project.pk,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트 또는 업무를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("task_update() 오류")

        messages.error(
            request,
            "업무 상태를 변경하는 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )
    

@login_required
def file_list(request, project_id):
    """
    프로젝트 파일 목록

    표시 정보
    - 프로젝트 정보
    - 업로드된 파일 목록
    - 파일 업로드 폼
    """

    try:

        # 프로젝트 조회 (참여자만 접근 가능)
        project = get_object_or_404(
            Project,
            pk=project_id,
            projectmember__user=request.user,
        )

        # 파일 목록
        files = (
            ProjectFile.objects.filter(
                project=project
            )
            .select_related(
                "uploader"
            )
            .order_by(
                "-uploaded_at"
            )
        )

        # 업로드 폼
        form = ProjectFileForm()

        context = {

            "project": project,

            "files": files,

            "form": form,

        }

        return render(
            request,
            "project/files.html",
            context,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("file_list() 오류")

        messages.error(
            request,
            "파일 목록을 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )
    
@require_POST
@login_required
def file_upload(request, project_id):
    """
    프로젝트 파일 업로드

    - 프로젝트 참여자만 업로드 가능
    - 업로더는 현재 로그인 사용자
    """

    try:

        # 프로젝트 조회 (참여자만 접근 가능)
        project = get_object_or_404(
            Project,
            pk=project_id,
            projectmember__user=request.user,
        )

        form = ProjectFileForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            project_file = form.save(commit=False)

            project_file.project = project

            project_file.uploader = request.user

            project_file.save()

            messages.success(
                request,
                "파일이 업로드되었습니다."
            )

        else:

            messages.error(
                request,
                "파일을 다시 확인해주세요."
            )

        return redirect(
            "project:file_list",
            project_id=project.pk,
        )

    except Http404:

        messages.error(
            request,
            "프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )

        return redirect(
            "project:project_list"
        )

    except Exception:

        logger.exception("file_upload() 오류")

        messages.error(
            request,
            "파일 업로드 중 오류가 발생했습니다."
        )

        return redirect(
            "project:project_list"
        )