# 1. 베이스 이미지
FROM python:3.12-slim

# 2. 환경 변수
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리
WORKDIR /app

# 4. 의존성 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 코드 복사
COPY . .

# 6. 포트 설정 (Render 기본)
EXPOSE 8000

# 7. 실행 명령 (Daphne)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]