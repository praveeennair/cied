from core.standard_responses import (
    success_response,
    general_error_response,
    not_found_response,
)
from core.models import (
    DeliveryAgent,
    Customer,
    Order,
    OTPRequests,
)
from management.serializers import (
    DeliveryAgentSerializer,
    CustomerSerializer,
    BlockCustomerSerializer,
    CustomerListSerializer,
    UpdateDeliveryStatusSerializer,
)
from core.constants import (
    UserGroups,
    Errormessages,
    OrderStatus,
)
from core.utils import (
    user_permission
)
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.views import APIView

from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import (
    SessionAuthentication,
)
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class DeliveryAgentListCreateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [user_permission([UserGroups.ADMIN])]
    serializer_class = DeliveryAgentSerializer
    http_method_names = ['get', 'post']

    def get(self, request):
        queryset = DeliveryAgent.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return success_response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username =  serializer.validated_data.get('user', {}).get('username')
            email = serializer.validated_data.get('email')
            password = get_random_string(length=14)

            if User.objects.filter(username=username).exists():
                return general_error_response({"error": "Username already exists"})

            user = User.objects.create_user(username=username, password=password, email=email)


            delivery_agent = DeliveryAgent.objects.create(
                user=user,
                name=serializer.validated_data['name'],
                phone_number=serializer.validated_data['phone_number'],
                email=serializer.validated_data['email'],
                is_active=serializer.validated_data['is_active'],
                is_blocked=serializer.validated_data['is_blocked']
            )
            agent_group = Group.objects.get(name=UserGroups.DELIVERY_AGENT)
            agent_group.user_set.add(user)
            data = {
                "id": delivery_agent.id,
                "name": delivery_agent.name,
                "username": user.username,
                "email": delivery_agent.email,
                "phone_number": delivery_agent.phone_number,
            }
            return success_response(data)

        return general_error_response({
            "error": serializer.errors
            })


class DeliveryAgentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = DeliveryAgent.objects.all()
    serializer_class = DeliveryAgentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [user_permission([UserGroups.ADMIN])]
    http_method_names = ['get', 'patch', 'delete']

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        delivery_agent_instance = self.get_object()
        user_instance = delivery_agent_instance.user

        if 'email' in validated_data or 'username' in validated_data:
            user_data = {key: validated_data[key] for key in ('email', 'username') if key in validated_data}

            if user_instance and user_data:
                for key, value in user_data.items():
                    setattr(user_instance, key, value)
                user_instance.save()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        user_to_delete = instance.user
        if user_to_delete:
            user_to_delete.delete()
        instance.delete()
        return success_response({'id': user_to_delete.id})


class CustomerListCreateAPIView(APIView):
    http_method_names = ['get', 'post']
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method == 'get':
            self.permission_classes = [user_permission([UserGroups.ADMIN])]
        else:
            self.permission_classes = []

        return super(CustomerListCreateAPIView, self).get_permissions()
    
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerListSerializer(customers, many=True)
        return success_response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username =  serializer.validated_data.get('user', {}).get('username')
            email = serializer.validated_data.get('email')
            password = get_random_string(length=14)
            if User.objects.filter(username=username).exists():
                return general_error_response({"error": "Username already exists"})

            user = User.objects.create_user(username=username, password=password, email=email)
            customer = Customer.objects.create(
                email=email,
                user=user,
                name=serializer.validated_data.get('name')
            )
            customer_group = Group.objects.get(name=UserGroups.CUSTOMER)
            customer_group.user_set.add(user)
            data = {
                'id': customer.id,
                'username': username,
                'name': customer.name,
                'email': customer.email

            }
            return success_response(data)
        return general_error_response(serializer.errors)


class BlockCustomerAPIView(APIView):
    serializer_class = BlockCustomerSerializer
    permission_classes = [user_permission([UserGroups.ADMIN])]
    authentication_classes = [SessionAuthentication]
    http_method_names = ['patch']

    def patch(self, request, pk):
        customer = Customer.objects.filter(pk=pk).first()

        if not customer:
            return not_found_response(Errormessages.NOT_FOUND)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            customer.is_blocked=serializer.validated_data.get('is_blocked')
            customer.save()
            return success_response(serializer.data)
        return general_error_response(Errormessages.FAILED)


class DeleteCustomerAPIView(APIView):
    permission_classes = [user_permission([UserGroups.CUSTOMER])]
    authentication_classes = [SessionAuthentication]
    http_method_names = ['delete']

    def delete(self, request, pk):
        customer = Customer.objects.filter(pk=pk, user=request.user).first()

        if not customer:
            return not_found_response(Errormessages.NOT_FOUND)
        
        pending_orders = Order.objects.all().exclude(
            status__in=(OrderStatus.DELIVERED, OrderStatus.CANCELLED)
        ).exists()
        if not pending_orders:
            customer.is_active = False
            customer.user.is_active=False
            customer.save()

            return success_response({'id': pk})
        return general_error_response(Errormessages.FAILED)


class UpdateDeliveryStatusAPIView(APIView):
    permission_classes = [user_permission([UserGroups.DELIVERY_AGENT])]
    authentication_classes = [SessionAuthentication]
    serializer_class = UpdateDeliveryStatusSerializer
    http_method_names = ['patch']

    def patch(self, request, pk):
        order = Order.objects.filter(pk=pk).first()

        if not order:
            return not_found_response(Errormessages.NOT_FOUND)

        otp_request = OTPRequests.objects.filter(order=order).last()

        if not otp_request():
            return general_error_response(Errormessages.FAILED)
        
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return general_error_response(Errormessages.FAILED)
        
        if otp_request == serializer.validated_data.get('otp'):
            order.status = OrderStatus.DELIVERED
            order.save()
            otp_request.is_used = True
            otp_request.save()
            return success_response({'id': order.id})
        return general_error_response(Errormessages.FAILED)