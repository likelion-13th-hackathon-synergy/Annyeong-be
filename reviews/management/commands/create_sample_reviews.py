#테스트용 샘플 데이터 생성 명령어
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reviews.models import Review
import random

User = get_user_model()


class Command(BaseCommand):
    help = '샘플 후기 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='생성할 사용자 수')
        parser.add_argument('--reviews', type=int, default=50, help='생성할 후기 수')

    def handle(self, *args, **options):
        # 테스트용 사용자 생성
        users = []
        for i in range(options['users']):
            username = f'testuser{i + 1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            users.append(user)
            if created:
                self.stdout.write(f'사용자 {username} 생성됨')

        # 테스트용 후기 생성
        personalities = [f'personality_{i}' for i in range(1, 11)]

        for i in range(options['reviews']):
            reviewer = random.choice(users)
            reviewed_user = random.choice(users)

            # 자기 자신에게 후기 작성 방지
            while reviewer == reviewed_user:
                reviewed_user = random.choice(users)

            # 중복 후기 방지
            if Review.objects.filter(reviewer=reviewer, reviewed_user=reviewed_user).exists():
                continue

            review = Review.objects.create(
                reviewer=reviewer,
                reviewed_user=reviewed_user
            )

            # 랜덤하게 1-3개의 성격 선택
            selected_count = random.randint(1, 3)
            selected_personalities = random.sample(personalities, selected_count)

            for personality in selected_personalities:
                setattr(review, personality, True)

            review.save()

        self.stdout.write(
            self.style.SUCCESS(f'샘플 데이터 생성 완료: 사용자 {len(users)}명, 후기 {Review.objects.count()}개')
        )

