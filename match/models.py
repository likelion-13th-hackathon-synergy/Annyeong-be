from django.db import models
from django.conf import settings

class UserMatchPreference(models.Model):
    # 매칭 모드 상수 정의
    MODE_JOB = 1        # 구인구직
    MODE_TRANS = 2      # 통역
    MODE_BUDDY = 3      # 버디
    MODE_DATE = 4       # 연애/데이팅
    MODE_SUPPORT = 5    # 서포터즈

    MODE_CHOICES = [
        (MODE_JOB, '구인구직'),
        (MODE_TRANS, '통역'),
        (MODE_BUDDY, '버디'),
        (MODE_DATE, '연애/데이팅'),
        (MODE_SUPPORT, '서포터즈'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mode = models.PositiveSmallIntegerField(choices=MODE_CHOICES, default=MODE_JOB)

    def __str__(self):
        # 유저 이름과 모드명 표시
        return f"{self.user.username} - {self.get_mode_display()}"


class MatchLike(models.Model):
    # 좋아요를 누른 유저 (from_user)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes_given', on_delete=models.CASCADE)
    # 좋아요를 받은 유저 (to_user)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes_received', on_delete=models.CASCADE)
    # 좋아요 생성 시간 기록
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        # 누가 누구에게 좋아요를 눌렀는지
        return f"Like: {self.from_user.username} -> {self.to_user.username}"


class MatchDislike(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dislikes_given', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dislikes_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"Dislike: {self.from_user.username} -> {self.to_user.username}"