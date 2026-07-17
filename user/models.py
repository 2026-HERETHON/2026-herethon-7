# user/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """회원"""
    email = models.EmailField(unique=True, verbose_name='이메일')
    name = models.CharField(max_length=50, verbose_name='이름')

    # email로 로그인
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    class Meta:
        db_table = 'user'
        verbose_name = '회원'

    def __str__(self):
        return self.name


class Talent(models.Model):
    """재능 (마스터 데이터)"""
    name = models.CharField(max_length=50, verbose_name='재능명')

    class Meta:
        db_table = 'talent'
        verbose_name = '재능'

    def __str__(self):
        return self.name


class Profile(models.Model):
    """프로필"""

    class Identity(models.TextChoices):
        EXPERIENCED = 'EXPERIENCED', '경험 보유자'
        STARTER = 'STARTER', '커리어 스타터'

    class WorkStyle(models.TextChoices):
        ONE = 'ONE', '1:1'
        GROUP = 'GROUP', '소그룹'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='회원')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='프로필사진')
    intro = models.TextField(blank=True, null=True, verbose_name='한줄소개')
    identity = models.CharField(max_length=20, choices=Identity.choices, verbose_name='정체성')
    work_style = models.CharField(max_length=10, choices=WorkStyle.choices, verbose_name='선호협업방식')
    skills = models.CharField(max_length=255, blank=True, null=True, verbose_name='기술태그')

    class Meta:
        db_table = 'profile'
        verbose_name = '프로필'

    def __str__(self):
        return f'{self.user.name}의 프로필'


class ProfileTalent(models.Model):
    """프로필재능 (기부재능 GIVE / 희망재능 NEED)"""

    class TalentType(models.TextChoices):
        GIVE = 'GIVE', '기부재능'
        NEED = 'NEED', '희망재능'

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='프로필')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, verbose_name='재능')
    type = models.CharField(max_length=10, choices=TalentType.choices, verbose_name='구분')

    class Meta:
        db_table = 'profile_talent'
        verbose_name = '프로필재능'
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'talent', 'type'],
                name='unique_profile_talent_type'
            )
        ]

    def __str__(self):
        return f'{self.profile.user.name} - {self.talent.name} ({self.type})'


class Portfolio(models.Model):
    """포트폴리오"""

    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, related_name='portfolios', verbose_name='프로젝트')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios', verbose_name='작성자')
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name='제목')
    role = models.TextField(blank=True, null=True, verbose_name='내 역할')
    summary = models.TextField(blank=True, null=True, verbose_name='요약')
    file_path = models.FileField(upload_to='portfolios/', blank=True, null=True, verbose_name='파일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'portfolio'
        verbose_name = '포트폴리오'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                name='unique_project_portfolio'
            )
        ]

    def __str__(self):
        return f'{self.user.name} - {self.project.title}'


class Review(models.Model):
    """리뷰"""
    project = models.ForeignKey(
        'project.Project', on_delete=models.CASCADE, verbose_name='프로젝트'
    )
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='written_reviews', verbose_name='작성자'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_reviews', verbose_name='수신자'
    )
    rating = models.IntegerField(verbose_name='평점')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일시')

    class Meta:
        db_table = 'review'
        verbose_name = '리뷰'

    def __str__(self):
        return f'{self.writer.name} → {self.receiver.name} ({self.rating}점)'