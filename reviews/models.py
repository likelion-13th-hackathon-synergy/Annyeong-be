from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviewer')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviewed_reviewer')

    #성격 선택(10개 중 최대 5개 다중선택 가능)
    personality_1 = models.BooleanField(default=False, verbose_name="성격문장 1")
    personality_2 = models.BooleanField(default=False, verbose_name="성격문장 2")
    personality_3 = models.BooleanField(default=False, verbose_name="성격문장 3")
    personality_4 = models.BooleanField(default=False, verbose_name="성격문장 4")
    personality_5 = models.BooleanField(default=False, verbose_name="성격문장 5")
    personality_6 = models.BooleanField(default=False, verbose_name="성격문장 6")
    personality_7 = models.BooleanField(default=False, verbose_name="성격문장 7")
    personality_8 = models.BooleanField(default=False, verbose_name="성격문장 8")
    personality_9 = models.BooleanField(default=False, verbose_name="성격문장 9")
    personality_10 = models.BooleanField(default=False, verbose_name="성격문장 10")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        #한 사람당 한 번만 후기 작성 가능
        unique_together = ['reviewer', 'reviewed_user']

    def __str__(self):
        return f'{self.reviewer.username} → {self.reviewed_user.username}'

    def get_selected_personalities(self):
        personalities = []
        if self.personality_1:
            personalities.append("성격1")
        if self.personality_2:
            personalities.append("성격2")
        if self.personality_3:
            personalities.append("성격3")
        if self.personality_4:
            personalities.append("성격4")
        if self.personality_5:
            personalities.append("성격5")
        if self.personality_6:
            personalities.append("성격6")
        if self.personality_7:
            personalities.append("성격7")
        if self.personality_8:
            personalities.append("성격8")
        if self.personality_9:
            personalities.append("성격9")
        if self.personality_10:
            personalities.append("성격10")
        return personalities


