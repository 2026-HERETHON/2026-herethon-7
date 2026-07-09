from django.db import models
from django.conf import settings


class Talent(models.Model):

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    


class Proposal(models.Model):
    class Mode(models.TextChoices):
        ONE = "ONE", "1:1"
        GROUP = "GROUP", "소그룹"

    class WeeklyTime(models.TextChoices):
        ONE_TO_FOUR = "ONE_TO_FOUR", "1~4시간"
        FIVE_TO_TEN = "FIVE_TO_TEN", "5~10시간"
        ELEVEN_TO_TWENTY = "ELEVEN_TO_TWENTY", "11~20시간"
        OVER_TWENTY = "OVER_TWENTY", "20시간 이상"

    class Communication(models.TextChoices):
        KAKAO = "KAKAO", "카카오톡"
        GOOGLE_MEET = "GOOGLE_MEET", "Google Meet"
        DISCORD = "DISCORD", "Discord"
        ETC = "ETC", "기타"

    class Status(models.TextChoices):
        WAIT = "WAIT", "대기"
        ACCEPT = "ACCEPT", "수락"
        REJECT = "REJECT", "거절"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_proposals"
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_proposals"
)

    talent = models.ForeignKey(
        Talent,
        on_delete=models.CASCADE,
        related_name="proposals"
    )

    title = models.CharField(max_length=100)

    goal = models.TextField()

    message = models.TextField(
        blank=True
    )

    mode = models.CharField(
        max_length=10,
        choices=Mode.choices
    )

    period = models.PositiveIntegerField(
        help_text="주 단위"
    )

    weekly_time = models.CharField(
        max_length=20,
        choices=WeeklyTime.choices
    )

    communication = models.CharField(
        max_length=20,
        choices=Communication.choices
    )

    attachment = models.FileField(
        upload_to="proposal/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.WAIT
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-created_at"]