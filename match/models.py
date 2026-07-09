# match/models.py

from django.db import models
from user.models import User, Talent


class Proposal(models.Model):
    """협업 제안"""

    class Mode(models.TextChoices):
        ONE = 'ONE', '1:1 교환형'
        GROUP = 'GROUP', '소그룹'

    class WeeklyTime(models.TextChoices):
        ONE_TO_FOUR = 'ONE_TO_FOUR', '1~4시간'
        FIVE_TO_TEN = 'FIVE_TO_TEN', '5~10시간'
        ELEVEN_TO_TWENTY = 'ELEVEN_TO_TWENTY', '11~20시간'
        OVER_TWENTY = 'OVER_TWENTY', '20시간 이상'

    class Communication(models.TextChoices):
        KAKAO = 'KAKAO', '카카오톡'
        GOOGLE_MEET = 'GOOGLE_MEET', '구글 미트'
        DISCORD = 'DISCORD', '디스코드'
        ETC = 'ETC', '기타'

    class Status(models.TextChoices):
        WAIT = 'WAIT', '대기'
        ACCEPT = 'ACCEPT', '수락'
        REJECT = 'REJECT', '거절'

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_proposals', verbose_name='발신자'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_proposals', verbose_name='수신자'
    )
    title = models.CharField(max_length=100, verbose_name='제목')
    goal = models.TextField(verbose_name='목표')
    message = models.TextField(blank=True, null=True, verbose_name='메시지')
    give_talent = models.ForeignKey(
        Talent, on_delete=models.CASCADE, related_name='give_proposals', verbose_name='기부재능'
    )
    need_talent = models.ForeignKey(
        Talent, on_delete=models.CASCADE, related_name='need_proposals', verbose_name='희망재능'
    )
    mode = models.CharField(max_length=10, choices=Mode.choices, verbose_name='협업모드')
    period = models.IntegerField(verbose_name='기간(주)')
    weekly_time = models.CharField(max_length=20, choices=WeeklyTime.choices, verbose_name='주당시간')
    communication = models.CharField(max_length=20, choices=Communication.choices, verbose_name='소통수단')
    attachment = models.FileField(upload_to='proposals/', blank=True, null=True, verbose_name='첨부파일')
    status = models.CharField(max_length=10, choices=Status.choices, default='WAIT', verbose_name='상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'proposal'
        verbose_name = '제안'

    def __str__(self):
        return f'{self.sender.name} → {self.receiver.name}: {self.title}'