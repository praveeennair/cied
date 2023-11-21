from django.urls import path
from core.views import (
    AdminHomeAPIView,
    ProductListAPIView,
    ProductAPIView,
)


urlpatterns = [
    path('', AdminHomeAPIView.as_view()),
    path('product/', ProductListAPIView.as_view(), name='get_products'),
    path('product/<int:pk>', ProductAPIView.as_view()),
]
