"""md-slides 설정. MD 강의안을 웹 슬라이드로 보여주는 작은 Django 프로젝트(DB·로그인 없음)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 개발용 기본값. 운영에서는 환경 변수로 바꾼다.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-md-slides-dev-only")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") != "0"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "slides",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "md_slides.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    },
]

WSGI_APPLICATION = "md_slides.wsgi.application"

# 강의안은 파일로만 관리하므로 DB를 쓰지 않는다.
DATABASES = {}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# 강의안(MD) 폴더. 환경 변수 SLIDES_DIR로 다른 폴더를 가리킬 수 있다.
SLIDES_DIR = Path(os.environ.get("SLIDES_DIR", BASE_DIR / "decks"))
