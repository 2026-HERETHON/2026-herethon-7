from collections import defaultdict
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404
from django.views.decorators.http import require_POST
from .models import Project, Task, ProjectFile
from user.models import Portfolio
from .forms import ProjectFileForm, ProjectOverviewForm, TaskForm
from .services import update_task_status

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
def project_overview_edit(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("proposal"),
        pk=project_id,
        projectmember__user=request.user,
    )

    if request.method == "POST":
        form = ProjectOverviewForm(
            request.POST,
            project=project,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "프로젝트 개요가 저장되었습니다.",
            )

            return redirect(
                "project:project_overview",
                project_id=project.id,
            )

    else:
        form = ProjectOverviewForm(
            project=project,
        )

    return render(
        request,
        "project/overview_form.html",
        {
            "project": project,
            "form": form,
        },
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
    


@login_required
def task_create(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        projectmember__user=request.user,
    )

    if request.method == "POST":
        form = TaskForm(
            request.POST,
            project=project,
        )

        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.status = Task.Status.TODO
            task.save()

            messages.success(
                request,
                "업무가 추가되었습니다.",
            )

            return redirect(
                "project:task_list",
                project_id=project.id,
            )

    else:
        form = TaskForm(project=project)

    return render(
        request,
        "project/task_form.html",
        {
            "project": project,
            "form": form,
        },
    )
    
@require_POST
@login_required
def task_update(request, project_id, task_id):
    """
    업무 상태 변경
    프로젝트 완료 여부 확인
    완료 시 포트폴리오 자동 생성

    Service로 비즈니스 로직 처리
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

        update_task_status(
            task=task,
            status=status,
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
            ProjectFile.objects.filter(project=project)
            .select_related("uploader")
            .order_by("folder_name", "-uploaded_at")
        )

        grouped_files = defaultdict(list)

        for file in files:
            folder = file.folder_name or "기타"
            grouped_files[folder].append(file)

        # 업로드 폼
        form = ProjectFileForm()

        context = {
            "project": project,
            "grouped_files": dict(grouped_files),
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
    
@login_required
def chat_room(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        projectmember__user=request.user,
    )

    return render(
        request,
        "project/chat.html",
        {
            "project": project,
        },
    )

