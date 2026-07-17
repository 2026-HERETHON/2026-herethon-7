from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch
from user.models import User, Profile, ProfileTalent
from match.models import Proposal
from match.forms import ProposalForm
from project.models import ProjectMember, Project
from django.http import Http404
import logging
from .services import accept_proposal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@login_required
def home(request):
    """
    홈 화면

    - 인사말
    - 내 재능(GIVE / NEED)
    - 진행 중 프로젝트
    """

    try:
        user = request.user

        # -----------------------------
        # 프로필 조회
        # -----------------------------
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = None

        # -----------------------------
        # 재능 조회
        # -----------------------------
        give_talents = []
        need_talents = []

        if profile:
            give_talents = ProfileTalent.objects.filter(
                profile=profile,
                type=ProfileTalent.TalentType.GIVE
            ).select_related("talent")

            need_talents = ProfileTalent.objects.filter(
                profile=profile,
                type=ProfileTalent.TalentType.NEED
            ).select_related("talent")

        # -----------------------------
        # 진행 중 프로젝트 조회
        # -----------------------------
        project_members = ProjectMember.objects.filter(
            user=user
        ).select_related("project")

        projects = Project.objects.filter(
            projectmember__user=user,
            status=Project.Status.IN_PROGRESS,
        ).distinct()

        context = {
            "profile": profile,
            "give_talents": give_talents,
            "need_talents": need_talents,
            "projects": projects,
        }

        # -----------------------------
        # templates/match/home.html
        # -----------------------------
        return render(
            request,
            "match/home.html",
            context
        )

    except Exception:
        logger.exception("home() 오류")

        messages.error(
            request,
            "홈 화면을 불러오는 중 오류가 발생했습니다."
        )

        return render(
            request,
            "match/home.html",
            {
                "profile": None,
                "give_talents": [],
                "need_talents": [],
                "projects": [],
            }
        )
    


@login_required
def matching_list(request):
    """
    추천 매칭 리스트

    추천 기준
    - 내 NEED 재능
    - 상대 GIVE 재능
    - 자기 자신 제외

    필터(GET)
    - identity : EXPERIENCED / STARTER
    - work_style : ONE / GROUP
    """

    try:

        # 현재 로그인 사용자
        me = request.user

        # ---------- 필터 값 ----------
        identity = request.GET.get("identity")
        work_style = request.GET.get("work_style")

        # ---------- 내 프로필 ----------
        try:
            my_profile = Profile.objects.get(user=me)

        except Profile.DoesNotExist:

            messages.warning(
                request,
                "프로필을 먼저 작성해주세요."
            )

            return render(
                request,
                "match/matching_list.html",
                {
                    "matching_users": [],
                    "selected_identity": identity,
                    "selected_work_style": work_style,
                }
            )

        # ---------- 내가 원하는 재능 ----------
        my_need_ids = list(

            ProfileTalent.objects.filter(
                profile=my_profile,
                type=ProfileTalent.TalentType.NEED
            ).values_list(
                "talent_id",
                flat=True
            )

        )

        if not my_need_ids:

            messages.info(
                request,
                "희망 재능을 먼저 등록해주세요."
            )

            return render(
                request,
                "match/matching_list.html",
                {
                    "matching_users": [],
                    "selected_identity": identity,
                    "selected_work_style": work_style,
                }
            )

        # ---------- 내 NEED를 GIVE하는 사용자 ----------
        matched_profile_ids = ProfileTalent.objects.filter(

            type=ProfileTalent.TalentType.GIVE,
            talent_id__in=my_need_ids

        ).values_list(
            "profile_id",
            flat=True
        )

        profiles = Profile.objects.filter(
            pk__in=matched_profile_ids
        ).exclude(
            user=me
        )

        # ======================================================
        # 필터 적용
        # ======================================================

        if identity in [
            Profile.Identity.EXPERIENCED,
            Profile.Identity.STARTER,
        ]:

            profiles = profiles.filter(
                identity=identity
            )

        if work_style in [
            Profile.WorkStyle.ONE,
            Profile.WorkStyle.GROUP,
        ]:

            profiles = profiles.filter(
                work_style=work_style
            )

        # ======================================================

        profiles = profiles.select_related(
            "user"
        ).prefetch_related(

            Prefetch(
                "profiletalent_set",
                queryset=ProfileTalent.objects.filter(
                    type=ProfileTalent.TalentType.GIVE
                ).select_related(
                    "talent"
                ),
                to_attr="give_talents"
            ),

            Prefetch(
                "profiletalent_set",
                queryset=ProfileTalent.objects.filter(
                    type=ProfileTalent.TalentType.NEED
                ).select_related(
                    "talent"
                ),
                to_attr="need_talents"
            ),

        )

        # 매칭 퍼센트 계산
        from .services import calculate_match_percent

        for profile in profiles:
            profile.match_percent = calculate_match_percent(
                request.user, profile.user
            )

        # 퍼센트 높은 순 정렬
        profiles = sorted(profiles, key=lambda p: p.match_percent, reverse=True)

        context = {

            "matching_users": profiles,

            # 현재 선택된 필터
            "selected_identity": identity,
            "selected_work_style": work_style,

        }

        return render(
            request,
            "match/matching_list.html",
            context
        )

    except Exception:
        logger.exception("matching_list() 오류")

        messages.error(
            request,
            "추천 매칭 목록을 불러오는 중 오류가 발생했습니다."
        )

        return render(
            request,
            "match/matching_list.html",
            {
                "matching_users": [],
                "selected_identity": None,
                "selected_work_style": None,
            }
        )

@login_required
def matching_detail(request, user_id):
    """
    추천 매칭 상세

    보여주는 정보
    - 프로필 사진
    - 이름
    - 한줄 소개
    - 경험 보유자/커리어 스타터
    - 협업 방식
    - GIVE 재능
    - NEED 재능

    버튼
    - 채팅 시작 (미구현)
    - 협업 제안 보내기
    """

    try:

        # 자기 자신은 조회하지 않음
        if request.user.id == user_id:

            messages.warning(
                request,
                "본인의 프로필입니다."
            )

            return redirect("match:matching_list")

        # 상대 회원 조회
        partner = get_object_or_404(
            User,
            pk=user_id
        )

        # 프로필 조회
        profile = get_object_or_404(

            Profile.objects.prefetch_related(

                Prefetch(
                    "profiletalent_set",
                    queryset=ProfileTalent.objects.filter(
                        type=ProfileTalent.TalentType.GIVE
                    ).select_related("talent"),
                    to_attr="give_talents"
                ),

                Prefetch(
                    "profiletalent_set",
                    queryset=ProfileTalent.objects.filter(
                        type=ProfileTalent.TalentType.NEED
                    ).select_related("talent"),
                    to_attr="need_talents"
                ),

            ),

            user=partner

        )

        context = {

            # 회원
            "partner": partner,

            # 프로필
            "profile": profile,

            # 재능 목록
            "give_talents": profile.give_talents,
            "need_talents": profile.need_talents,

            # 버튼에서 사용할 값
            "receiver": partner,

            # 추후 chat 기능 개발 시
            #"can_chat": False,

        }

        return render(
            request,
            "match/matching_detail.html",
            context
        )

    except Http404:

        messages.error(
            request,
            "존재하지 않는 사용자입니다."
        )

        return redirect("match:matching_list")

    except Exception:
        logger.exception("matching_detail() 오류")

        messages.error(
            request,
            "매칭 정보를 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:matching_list"
        )
    
@login_required
def proposal_create(request, receiver_id):
    """
    협업 제안 작성

    GET
    - 제안 작성 폼

    POST
    - 제안 저장
    - sender = 로그인 사용자
    - receiver = 선택한 사용자
    """

    try:
        # -----------------------------
        # 제안 받을 사용자 조회
        # -----------------------------
        receiver = get_object_or_404(
            User,
            pk=receiver_id
        )

        # -----------------------------
        # 자기 자신에게 제안 금지
        # -----------------------------
        if receiver == request.user:

            messages.warning(
                request,
                "본인에게는 협업 제안을 보낼 수 없습니다."
            )

            return redirect(
                "match:matching_list"
            )
        
        if Proposal.objects.filter(
            sender=request.user,
            receiver=receiver,
            status=Proposal.Status.WAIT
        ).exists():

            messages.warning(
                request,
                "이미 응답을 기다리는 협업 제안이 있습니다."
            )

            return redirect(
                "match:matching_detail",
                user_id=receiver.pk
            )

        # -----------------------------
        # GET
        # -----------------------------
        if request.method == "GET":

            form = ProposalForm()

            return render(
                request,
                "match/proposal_form.html",
                {
                    "form": form,
                    "receiver": receiver,
                }
            )

        # -----------------------------
        # POST
        # -----------------------------
        form = ProposalForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            proposal = form.save(
                commit=False
            )

            proposal.sender = request.user
            proposal.receiver = receiver

            proposal.save()

            messages.success(
                request,
                "협업 제안을 전송했습니다."
            )

            return redirect(
                "match:proposal_complete",
                proposal_id=proposal.pk
            )

        # -----------------------------
        # 입력 오류
        # -----------------------------
        messages.error(
            request,
            "입력한 내용을 다시 확인해주세요."
        )

        return render(
            request,
            "match/proposal_form.html",
            {
                "form": form,
                "receiver": receiver,
            }
        )

    except Http404:

        messages.error(
            request,
            "존재하지 않는 사용자입니다."
        )

        return redirect(
            "match:matching_list"
        )

    except Exception:
        logger.exception("proposal_create() 오류")

        messages.error(
            request,
            "협업 제안을 작성하는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:matching_list"
        )
    

@login_required
def proposal_complete(request, proposal_id):
    """
    협업 제안 전송 완료

    - 방금 보낸 제안 내용 확인
    - 제안 조건 요약
    """

    try:

        proposal = get_object_or_404(
            Proposal.objects.select_related(
                "sender",
                "receiver",
                "give_talent",
                "need_talent",
            ),
            pk=proposal_id,
        )

        # 본인이 보낸 제안만 조회 가능
        if proposal.sender != request.user:

            messages.error(
                request,
                "접근 권한이 없습니다."
            )

            return redirect(
                "match:matching_list"
            )

        context = {
            "proposal": proposal,
        }

        return render(
            request,
            "match/proposal_complete.html",
            context,
        )

    except Http404:

        messages.error(
            request,
            "존재하지 않는 협업 제안입니다."
        )

        return redirect(
            "match:matching_list"
        )

    except Exception:

        logger.exception(
            "proposal_complete() 오류"
        )

        messages.error(
            request,
            "제안 정보를 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:matching_list"
        )
    
@login_required
def proposal_received_list(request):
    """
    받은 협업 제안 목록

    표시 정보
    - 제안자
    - 제목
    - 기부 재능
    - 희망 재능
    - 상태
    - 생성일
    """

    try:

        proposals = (
            Proposal.objects.filter(
                receiver=request.user
            )
            .select_related(
                "sender",
                "receiver",
                "give_talent",
                "need_talent",
            )
            .order_by("-created_at")
        )

        context = {
            "proposals": proposals,
        }

        return render(
            request,
            "match/received_list.html",
            context,
        )

    except Exception:

        logger.exception(
            "proposal_received_list() 오류"
        )

        messages.error(
            request,
            "받은 제안 목록을 불러오는 중 오류가 발생했습니다."
        )

        return render(
            request,
            "match/received_list.html",
            {
                "proposals": [],
            },
        )

@login_required
def proposal_detail(request, proposal_id):
    """
    받은 협업 제안 상세

    표시 정보
    - 제안자
    - 기부 재능
    - 희망 재능
    - 제목
    - 목표
    - 메시지
    - 협업 방식
    - 기간
    - 주당 시간
    - 소통 방식
    - 첨부파일
    - 상태

    WAIT 상태인 경우
    - 수락 버튼
    - 거절 버튼
    """

    try:

        proposal = get_object_or_404(

            Proposal.objects.select_related(
                "sender",
                "receiver",
                "give_talent",
                "need_talent",
            ),

            pk=proposal_id,

        )

        # 받은 제안만 조회 가능
        if proposal.receiver != request.user:

            messages.error(
                request,
                "접근 권한이 없습니다."
            )

            return redirect(
                "match:proposal_received_list"
            )

        context = {

            "proposal": proposal,

            # 버튼 표시 여부
            "can_reply": (
                proposal.status == Proposal.Status.WAIT
            ),

        }

        return render(
            request,
            "match/proposal_detail.html",
            context
        )

    except Http404:

        messages.error(
            request,
            "존재하지 않는 협업 제안입니다."
        )

        return redirect(
            "match:proposal_received_list"
        )

    except Exception:

        logger.exception(
            "proposal_detail() 오류"
        )

        messages.error(
            request,
            "제안 정보를 불러오는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:proposal_received_list"
        )
    
@login_required
def proposal_accept(request, proposal_id):
    """
    협업 제안 수락 후 프로젝트&멤버 생성

    Service로 비즈니스 로직 처리 
    """

    if request.method != "POST":

        messages.error(
            request,
            "잘못된 요청입니다."
        )

        return redirect(
            "match:proposal_received_list"
        )

    try:

        proposal = get_object_or_404(
            Proposal.objects.select_related(
                "sender",
                "receiver",
            ),
            pk=proposal_id,
        )

        # 받은 사람만 수락 가능
        if proposal.receiver != request.user:

            messages.error(
                request,
                "권한이 없습니다."
            )

            return redirect(
                "match:proposal_received_list"
            )

        # 이미 처리된 제안인지 확인
        if proposal.status != Proposal.Status.WAIT:

            messages.warning(
                request,
                "이미 처리된 제안입니다."
            )

            return redirect(
                "match:proposal_detail",
                proposal_id=proposal.id,
            )

        project = accept_proposal(proposal)

        messages.success(
            request,
            "협업 제안을 수락했습니다."
        )

        return redirect(
            "project:project_overview",
            project_id=project.id,
        )

    except Http404:

        messages.error(
            request,
            "존재하지 않는 협업 제안입니다."
        )

        return redirect(
            "match:proposal_received_list"
        )

    except Exception:

        logger.exception(
            "proposal_accept() 오류"
        )

        messages.error(
            request,
            "제안을 수락하는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:proposal_received_list"
        )
    
from django.views.decorators.http import require_POST


@require_POST
@login_required
def proposal_reject(request, proposal_id):
    """
    협업 제안 거절

    - 받은 제안만 거절 가능
    - 상태를 REJECT로 변경
    - 받은 제안 목록으로 이동
    """

    try:

        proposal = get_object_or_404(
            Proposal,
            pk=proposal_id,
        )

        # 받은 제안만 처리 가능
        if proposal.receiver != request.user:

            messages.error(
                request,
                "권한이 없습니다."
            )

            return redirect(
                "match:proposal_received_list"
            )

        # 이미 처리된 제안
        if proposal.status != Proposal.Status.WAIT:

            messages.warning(
                request,
                "이미 처리된 제안입니다."
            )

            return redirect(
                "match:proposal_detail",
                proposal_id=proposal.pk,
            )

        # 거절
        proposal.status = Proposal.Status.REJECT
        proposal.save()

        messages.success(
            request,
            "협업 제안을 거절했습니다."
        )

        return redirect(
            "match:proposal_received_list"
        )

    except Exception:

        logger.exception("proposal_reject() 오류")

        messages.error(
            request,
            "제안을 거절하는 중 오류가 발생했습니다."
        )

        return redirect(
            "match:proposal_received_list"
        )

