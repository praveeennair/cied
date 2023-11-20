from django.urls import path
from core.views import AdminHomeAPIView
urlpatterns = [
    path('', AdminHomeAPIView.as_view()),
]
