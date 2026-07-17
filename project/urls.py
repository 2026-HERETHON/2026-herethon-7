from django.urls import path
from . import views

app_name = "project"

urlpatterns = [

    # ==========================
    # 프로젝트 목록
    # ==========================

    path(
        "projects/",
        views.project_list,
        name="project_list",
    ),

    # ==========================
    # 워크스페이스
    # ==========================

   # 워크스페이스 개요 화면
path(
    "projects/<int:project_id>/",
    views.project_overview,
    name="project_overview",
),

# 워크스페이스 개요 입력·수정 화면
path(
    "projects/<int:project_id>/edit/",
    views.project_overview_edit,
    name="project_overview_edit",
),

    # ==========================
    # 업무(Task)
    # ==========================

    path(
        "projects/<int:project_id>/tasks/",
        views.task_list,
        name="task_list",
    ),

    path(
        "projects/<int:project_id>/tasks/create/",
        views.task_create,
        name="task_create",
    ),

    path(
        "projects/<int:project_id>/tasks/<int:task_id>/update/",
        views.task_update,
        name="task_update",
    ),

    # ==========================
    # 파일
    # ==========================

    path(
        "projects/<int:project_id>/files/",
        views.file_list,
        name="file_list",
    ),

    path(
        "projects/<int:project_id>/files/upload/",
        views.file_upload,
        name="file_upload",
    ),

    # ==========================
    # 채팅
    # ==========================

    path(
        "projects/<int:project_id>/chat/",
        views.chat_room,
        name="chat_room",
    ),

#    path(
#        "projects/<int:project_id>/chat/send/",
#        views.chat_send,
#        name="chat_send",
#    ),


]