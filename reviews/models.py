from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviewer')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviewed_reviewer')

    #성격 선택(10개 중 최대 5개 다중선택 가능)
    personality_1 = models.BooleanField(default=False, verbose_name="이야기를 잘 들어줘요 1")
    personality_2 = models.BooleanField(default=False, verbose_name="유머 감각이 뛰어나요")
    personality_3 = models.BooleanField(default=False, verbose_name="대화가 재미있어요")
    personality_4 = models.BooleanField(default=False, verbose_name="긍정적인 마인드예요")
    personality_5 = models.BooleanField(default=False, verbose_name="친근하고 따뜻해요")
    personality_6 = models.BooleanField(default=False, verbose_name="배려심이 깊어요")
    personality_7 = models.BooleanField(default=False, verbose_name="지식이 풍부해요")
    personality_8 = models.BooleanField(default=False, verbose_name="호기심이 많아요")
    personality_9 = models.BooleanField(default=False, verbose_name="이해심이 많아요")
    personality_10 = models.BooleanField(default=False, verbose_name="정직하고 솔직해요")
    personality_11 = models.BooleanField(default=False, verbose_name="적극적이고 활발해요")
    personality_12 = models.BooleanField(default=False, verbose_name="신뢰할 수 있어요")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        #한 사람당 한 번만 후기 작성 가능
        unique_together = ['reviewer', 'reviewed_user']

    def __str__(self):
        return f'{self.reviewer.username} → {self.reviewed_user.username}'

    def get_selected_personalities(self):
        personalities = []
        personality_mapping = {
            'personality_1': '이야기를 잘 들어줘요',
            'personality_2': '유머 감각이 뛰어나요',
            'personality_3': '대화가 재미있어요',
            'personality_4': '긍적적인 마인드예요',
            'personality_5': '친근하고 따뜻해요',
            'personality_6': '배려심이 깊어요',
            'personality_7': '지식이 풍부해요',
            'personality_8': '호기심이 많아요',
            'personality_9': '이해심이 많아요',
            'personality_10': '정직하고 솔직해요',
            'personality_11': '적극적이고 활발해요',
            'personality_12': '신뢰할 수 있어요',

        }

        for field, label in personality_mapping.items():
            if getattr(self, field):
                personalities.append(label)
        return personalities


