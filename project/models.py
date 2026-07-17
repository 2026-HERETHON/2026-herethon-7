# project/models.py

from django.db import models
from user.models import User
from match.models import Proposal


class Project(models.Model):
    """프로젝트"""

    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'

    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, verbose_name='제안')
    title = models.CharField(max_length=100, verbose_name='프로젝트명')
    progress = models.IntegerField(default=0, verbose_name='진행률')
    status = models.CharField(max_length=20, choices=Status.choices, default='IN_PROGRESS', verbose_name='상태')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    overview_completed = models.BooleanField(
    default=False,
    verbose_name="개요 작성 완료 여부",
)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'project'
        verbose_name = '프로젝트'

    def __str__(self):
        return self.title


class ProjectMember(models.Model):
    """프로젝트 멤버"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='프로젝트')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='회원')
    role = models.CharField(max_length=50, blank=True, null=True, verbose_name='역할')

    class Meta:
        db_table = 'project_member'
        verbose_name = '프로젝트멤버'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                name='unique_project_member'
            )
        ]

    def __str__(self):
        return f'{self.project.title} - {self.user.name}'


class Task(models.Model):
    """할일"""

    class Status(models.TextChoices):
        TODO = 'TODO', '할일'
        DOING = 'DOING', '진행중'
        DONE = 'DONE', '완료'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='프로젝트')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='담당자')
    title = models.CharField(max_length=100, verbose_name='제목')
    deadline = models.DateField(blank=True, null=True, verbose_name='마감일')
    description = models.TextField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name="설명",
)
    status = models.CharField(max_length=10, choices=Status.choices, default='TODO', verbose_name='상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'task'
        verbose_name = '할일'

    def __str__(self):
        return self.title


class ProjectFile(models.Model):
    """프로젝트 파일"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='프로젝트')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='업로더')
    file_path = models.FileField(upload_to='project_files/', verbose_name='파일')
    folder_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='폴더명')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')

    class Meta:
        db_table = 'project_file'
        verbose_name = '프로젝트파일'

    def __str__(self):
        return f'{self.project.title} - {self.file_path.name}'


class ChatMessage(models.Model):
    """채팅메시지"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='프로젝트')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='전송일시')

    class Meta:
        db_table = 'chatMessage'
        verbose_name = '채팅메시지'
        ordering = ['sent_at']

    def __str__(self):
        return f'{self.sender.name}: {self.content[:20]}'
