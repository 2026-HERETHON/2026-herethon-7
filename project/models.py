from django.db import models
from django.conf import settings
from match.models import Proposal


class Project(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "진행중"
        COMPLETED = "COMPLETED", "완료"

    proposal = models.OneToOneField(
        Proposal,
        on_delete=models.CASCADE,
        related_name="project"
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )

    start_date = models.DateField()

    end_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.proposal.title
    
    class Meta:
        ordering = ["-created_at"]


class ProjectMember(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships"
    )

    role = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.project}"


class Task(models.Model):

    class Status(models.TextChoices):
        TODO = "TODO", "할 일"
        DOING = "DOING", "진행 중"
        DONE = "DONE", "완료"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(
        max_length=100
    )

    deadline = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.TODO
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title
    class Meta:
        ordering = ["-created_at"]


class ProjectFile(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="files"
    )

    file = models.FileField(
        upload_to="project/"
    )

    folder_name = models.CharField(
        max_length=100,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.file.name
    class Meta:
        ordering = ["-uploaded_at"]


class Portfolio(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="portfolio"
    )

    title = models.CharField(
        max_length=100,
        blank=True
    )

    role = models.TextField(
        blank=True
    )

    summary = models.TextField(
        blank=True
    )

    file = models.FileField(
        upload_to="portfolio/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title or f"Portfolio #{self.pk}"
    class Meta:
        ordering = ["-created_at"]


class Review(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews"
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews"
    )

    rating = models.PositiveSmallIntegerField()

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.writer} → {self.receiver}"
    class Meta:
        ordering = ["-created_at"]
