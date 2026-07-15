from django.urls import path
from . import views

app_name = "match"

urlpatterns = [

    # 홈
    path(
        "home/",
        views.home,
        name="home",
    ),

    # ==========================
    # 매칭
    # ==========================

    path(
        "matching/",
        views.matching_list,
        name="matching_list",
    ),

    path(
        "matching/<int:user_id>/",
        views.matching_detail,
        name="matching_detail",
    ),

    # ==========================
    # 협업 제안
    # ==========================

    path(
        "proposal/create/<int:receiver_id>/",
        views.proposal_create,
        name="proposal_create",
    ),

    path(
        "proposal/<int:proposal_id>/complete/",
        views.proposal_complete,
        name="proposal_complete",
    ),

    # 받은 제안 목록
    path(
        "proposal/received/",
        views.proposal_received_list,
        name="proposal_received_list",
    ),

    # 받은 제안 상세
    path(
        "proposal/<int:proposal_id>/",
        views.proposal_detail,
        name="proposal_detail",
    ),

    # 제안 수락
    path(
        "proposal/<int:proposal_id>/accept/",
        views.proposal_accept,
        name="proposal_accept",
    ),

    # 제안 거절
    path(
        "proposal/<int:proposal_id>/reject/",
        views.proposal_reject,
        name="proposal_reject",
    ),

]