from django.urls import path
from .views import (
    DeliveryAgentListCreateAPIView,
    DeliveryAgentDetailView,
    CustomerListCreateAPIView,
    BlockCustomerAPIView,
    DeleteCustomerAPIView,
    UpdateDeliveryStatusAPIView,
)

urlpatterns = [
    path('', DeliveryAgentListCreateAPIView.as_view(), name='delivery_agents_list_create'),
    path('<int:pk>/', DeliveryAgentDetailView.as_view(), name='delivery_agent_detail'),
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', BlockCustomerAPIView.as_view(), name='block_customer'),
    path('delete-customer/<int:pk>/', DeleteCustomerAPIView.as_view(), name='delete_customer'),
    path('update-order-status/<int:pk>/', UpdateDeliveryStatusAPIView.as_view(), name='update-delivery-status'),
]