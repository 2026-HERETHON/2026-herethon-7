from django.urls import path
from . import views

app_name = "match"

urlpatterns = [

    # 추천 매칭 리스트
    path(
        "",
        views.match_list,
        name="match_list"
    ),

    # 매칭 상세(프로필)
    path(
        "<int:user_id>/",
        views.match_detail,
        name="match_detail"
    ),



    # 협업 제안 작성
    path(
        "<int:user_id>/proposal/create/",
        views.proposal_create,
        name="proposal_create"
    ),

    # 제안 전송 완료
    path(
        "proposal/<int:proposal_id>/complete/",
        views.proposal_complete,
        name="proposal_complete"
    ),



    # 받은 제안 목록
    path(
        "proposal/received/",
        views.proposal_received,
        name="proposal_received"
    ),

    # 제안 수락
    path(
        "proposal/<int:proposal_id>/accept/",
        views.proposal_accept,
        name="proposal_accept"
    ),

    # 제안 거절
    path(
        "proposal/<int:proposal_id>/reject/",
        views.proposal_reject,
        name="proposal_reject"
    ),



    path(
        "proposal/<int:proposal_id>/accepted/",
        views.proposal_accepted,
        name="proposal_accepted"
    ),

]