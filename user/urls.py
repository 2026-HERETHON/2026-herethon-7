# user/urls.py

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 서비스 소개
    path('', views.index, name='index'),

    # 회원가입
    path('signup/', views.signup, name='signup'),
    path('signup/email-verify/', views.email_verify_send, name='email_verify_send'),
    path('signup/email-verify/confirm/', views.email_verify_confirm, name='email_verify_confirm'),
    path('signup/complete/', views.signup_complete, name='signup_complete'),

    # 로그인/로그아웃
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 비밀번호 찾기
    path('password/find/', views.password_find, name='password_find'),

    # 프로필
    path('profile/create/', views.profile_create, name='profile_create'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # 마이페이지
    path('mypage/', views.mypage_home, name='mypage_home'),

    # 포트폴리오
    path('mypage/portfolio/', views.portfolio_list, name='portfolio_list'),
    path('mypage/portfolio/<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('mypage/portfolio/<int:portfolio_id>/edit/', views.portfolio_edit, name='portfolio_edit'),

    # 후기
    path('mypage/reviews/', views.review_list, name='review_list'),
    path('mypage/reviews/create/<int:project_id>/', views.review_create, name='review_create'),
]