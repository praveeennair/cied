from django.urls import path
from core.views import (
    AdminHomeAPIView,
    ProductListAPIView,
    ProductAPIView,
    OrderListCreateAPIView,
    CancelOrderAPIView,
)


urlpatterns = [
    path('', AdminHomeAPIView.as_view()),
    path('product/', ProductListAPIView.as_view(), name='get_products'),
    path('product/<int:pk>', ProductAPIView.as_view(), name='product'),
    path('orders/', OrderListCreateAPIView.as_view({"get": "get_all"}),
         name='orders'),
    path('orders/<int:pk>',
         OrderListCreateAPIView.as_view({"get": "get", "post": "post"})),
    path('cancel-order/<int:pk>',
         CancelOrderAPIView.as_view(), name='cancel_order'),
]
