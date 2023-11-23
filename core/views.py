import random
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from core.standard_responses import (
    success_response,
    general_error_response,
    not_found_response,
)
from core.models import (
    Customer,
    Product,
    Order,
    OTPRequests,
)
from core.serializers import (
    ProductSerializer,
    OrderSerializer,
    # CancelOrderSerializer,
)
from core.constants import (
    UserGroups,
    Errormessages,
    OrderStatus
)
from core.utils import (
    user_permission
)
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import (
    SessionAuthentication,
)
from rest_framework.viewsets import ViewSet

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class AdminHomeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response('<h1> Home </h1>')


class ProductListAPIView(ListCreateAPIView):
    # permission_classes = [crm_permission([JuloUserRoles.CS_ADMIN])]
    serializer_class = ProductSerializer
    pagination_class = LargeResultsSetPagination
    queryset = Product.objects.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return success_response(response.data)


class ProductAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    serializer_class = ProductSerializer
    http_method_names = ['get', 'patch', 'delete']

    def get_permissions(self):
        if self.request.method == 'get':
            self.permission_classes = [user_permission([UserGroups.ADMIN, UserGroups.CUSTOMER])]
        else:
            self.permission_classes = [user_permission([UserGroups.ADMIN])]

        return super(ProductAPIView, self).get_permissions()

    def get(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return not_found_response(Errormessages.NOT_FOUND)
        serializer = self.serializer_class(instance=product)
        return success_response(serializer.data)
    
    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return not_found_response(Errormessages.NOT_FOUND)

        serializer = self.serializer_class(instance=product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)
        return general_error_response(Errormessages.FAILED)

    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return not_found_response(Errormessages.NOT_FOUND)

        product.delete()
        return success_response({'id': product.id})



class OrderListCreateAPIView(ViewSet):
    authentication_classes = [SessionAuthentication]
    serializer_class = OrderSerializer

    def get_all(self, request, format=None):
        orders = Order.objects.filter(customer__user=request.user).all()
        if not orders:
            return general_error_response(Errormessages.NO_ORDERS_EXISTS)
        serializer = self.serializer_class(orders, many=True)
        return success_response(serializer.data)
    
    def get(self, request, pk, format=None):
        orders = Order.objects.filter(customer=request.customer, id=pk)
        if not orders:
            return general_error_response(Errormessages.NO_ORDERS_EXISTS)
        serializer = self.serializer_class(orders)
        return success_response(serializer.data)

    def post(self, request):
        customer = Customer.objects.filter(user=request.user).last()
        if not customer:
            return general_error_response(Errormessages.NO_CUSTOMER_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            products = serializer.validated_data.get('products')
            total_price = 0
            for product in products:
                total_price += product.price
            orders = Order.objects.create(
                customer=customer,
                total_amount=total_price,
                status=OrderStatus.PENDING
                
            )
            orders.products.set(products)
            OTPRequests.objects.create(
                order=orders,
                otp_token=random.randint(100000, 999999),
                is_used=False
            )
            serializer.data.update({"id": orders.id})
            return success_response(serializer.data)
        return general_error_response(serializer.errors)
    
    
class CancelOrderAPIView(APIView):
    permission_classes = [user_permission([UserGroups.CUSTOMER])]
    authentication_classes = [SessionAuthentication]
    http_method_names = ['patch']

    def patch(self, request, pk):
        order = Order.objects.filter(pk=pk, customer__user=request.user).last()
        if not order:
            return not_found_response(Errormessages.NOT_FOUND)

        cdate = order.cdate
        end_date = cdate + timedelta(minutes=30)
        if cdate <= end_date:
            order.status=OrderStatus.CANCELLED
            order.save()
            data = {
                'id': order.id,
                'status': order.status
            }
            return success_response(data)
        return general_error_response(Errormessages.FAILED)

