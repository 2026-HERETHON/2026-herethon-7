from django.shortcuts import render

# Create your views here.
# user/views.py

import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile, ProfileTalent, Talent, Portfolio, Review
from .forms import SignupForm, LoginForm, ProfileForm, PasswordFindForm, PortfolioForm, ReviewForm

User = get_user_model()


# ========== 서비스 소개 ==========

def index(request):
    """서비스 소개 페이지"""
    return render(request, 'index.html')


# ========== 회원가입 ==========

def signup(request):
    """회원가입"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('user:login')
    else:
        form = SignupForm()
    return render(request, 'user/signup.html', {'form': form})


def email_verify_send(request):
    """이메일 인증코드 발송"""
    if request.method == 'POST':
        email = request.POST.get('email')
        # 6자리 인증코드 생성
        code = ''.join(random.choices(string.digits, k=6))
        # 세션에 저장 (3분 유효)
        request.session['verify_code'] = code
        request.session['verify_email'] = email

        # TODO: 실제 이메일 발송 로직 (해커톤에서는 콘솔 출력으로 대체)
        print(f'[인증코드] {email}: {code}')

        messages.info(request, '인증코드가 발송되었습니다.')
    return redirect('user:signup')


def email_verify_confirm(request):
    """이메일 인증코드 확인"""
    if request.method == 'POST':
        input_code = request.POST.get('code')
        saved_code = request.session.get('verify_code')

        if input_code == saved_code:
            request.session['email_verified'] = True
            messages.success(request, '이메일 인증이 완료되었습니다.')
        else:
            messages.error(request, '인증코드가 일치하지 않습니다.')
    return redirect('user:signup')


# ========== 로그인/로그아웃 ==========

def login_view(request):
    """로그인"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                # 자동 로그인 체크 안 하면 브라우저 닫을 때 세션 만료
                if not request.POST.get('remember_me'):
                    request.session.set_expiry(0)

                # 프로필 없으면 프로필 등록으로
                if not hasattr(user, 'profile'):
                    return redirect('user:profile_create')
                return redirect('match:home')
            else:
                messages.error(request, '이메일 또는 비밀번호가 올바르지 않습니다.')
    else:
        form = LoginForm()
    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    """로그아웃"""
    if request.method == 'POST':
        logout(request)
    return redirect('user:login')


# ========== 비밀번호 찾기 ==========

def password_find(request):
    """비밀번호 찾기 - 임시 비밀번호 발송"""
    if request.method == 'POST':
        form = PasswordFindForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # 임시 비밀번호 생성
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                user.set_password(temp_password)
                user.save()

                # TODO: 실제 이메일 발송 (해커톤에서는 콘솔 출력으로 대체)
                print(f'[임시 비밀번호] {email}: {temp_password}')

                messages.success(request, '임시 비밀번호가 이메일로 발송되었습니다.')
                return redirect('user:login')
            except User.DoesNotExist:
                messages.error(request, '가입되지 않은 이메일입니다.')
    else:
        form = PasswordFindForm()
    return render(request, 'user/password_find.html', {'form': form})


# ========== 프로필 ==========

@login_required
def profile_create(request):
    """프로필 등록"""
    # 이미 프로필 있으면 수정으로 리다이렉트
    if hasattr(request.user, 'profile'):
        return redirect('user:profile_edit')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 등록되었습니다.')
            return redirect('match:home')
    else:
        form = ProfileForm(user=request.user)

    talents = Talent.objects.all()
    return render(request, 'user/profile_form.html', {
        'form': form,
        'talents': talents,
        'is_edit': False,
    })


@login_required
def profile_edit(request):
    """프로필 수정"""
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('user:mypage_home')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    talents = Talent.objects.all()
    return render(request, 'user/profile_form.html', {
        'form': form,
        'talents': talents,
        'is_edit': True,
    })


# ========== 마이페이지 ==========

@login_required
def mypage_home(request):
    """마이페이지 홈"""
    user = request.user
    profile = getattr(user, 'profile', None)

    context = {
        'user': user,
        'profile': profile,
        'project_count': user.projectmember_set.filter(project__status='IN_PROGRESS').count() if profile else 0,
        'review_count': user.received_reviews.count() if profile else 0,
    }
    return render(request, 'user/mypage.html', context)


# ========== 포트폴리오 ==========

@login_required
def portfolio_list(request):
    """포트폴리오 목록"""
    # 내가 참여한 완료 프로젝트의 포트폴리오
    portfolios = Portfolio.objects.filter(
        project__projectmember__user=request.user
    ).select_related('project')
    return render(request, 'user/portfolio_list.html', {'portfolios': portfolios})


@login_required
def portfolio_detail(request, portfolio_id):
    """포트폴리오 상세"""
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
    is_owner = portfolio.project.projectmember_set.filter(user=request.user).exists()
    return render(request, 'user/portfolio_detail.html', {
        'portfolio': portfolio,
        'is_owner': is_owner,
    })


@login_required
def portfolio_edit(request, portfolio_id):
    """포트폴리오 수정"""
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id)

    # 본인 포트폴리오인지 확인
    if not portfolio.project.projectmember_set.filter(user=request.user).exists():
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('user:portfolio_list')

    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, '포트폴리오가 수정되었습니다.')
            return redirect('user:portfolio_detail', portfolio_id=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'user/portfolio_form.html', {'form': form, 'portfolio': portfolio})


# ========== 후기 ==========

@login_required
def review_list(request):
    """후기 목록"""
    written_reviews = request.user.written_reviews.all().select_related('project', 'receiver')
    received_reviews = request.user.received_reviews.all().select_related('project', 'writer')
    return render(request, 'user/review_list.html', {
        'written_reviews': written_reviews,
        'received_reviews': received_reviews,
    })


@login_required
def review_create(request, project_id):
    """후기 작성"""
    from project.models import Project
    project = get_object_or_404(Project, pk=project_id)

    # 프로젝트 멤버 중 나를 제외한 상대방
    other_members = project.projectmember_set.exclude(user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        receiver_id = request.POST.get('receiver_id')

        if form.is_valid() and receiver_id:
            review = form.save(commit=False)
            review.project = project
            review.writer = request.user
            review.receiver = get_object_or_404(User, pk=receiver_id)
            review.save()
            messages.success(request, '후기가 작성되었습니다.')
            return redirect('user:review_list')
    else:
        form = ReviewForm()

    return render(request, 'user/review_form.html', {
        'form': form,
        'project': project,
        'other_members': other_members,
    })