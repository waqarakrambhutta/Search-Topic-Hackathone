# myapp/urls.py
from django.urls import path
from .views import ArticleSummaryAPIView

urlpatterns = [
    path('generate-content/', ArticleSummaryAPIView.as_view(), name='generate-content'),
]
