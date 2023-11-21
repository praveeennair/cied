from rest_framework.views import APIView
from rest_framework.response import Response
from core.standard_responses import (
    success_response,
    general_error_response,
    not_found_response,
)
from core.models import (
    Product,
)
from core.serializers import (
    ProductSerializer
)
from core.constants import (
    UserGroups,
    Errormessages,
)
from core.utils import (
    user_permission
)
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import (
    SessionAuthentication,
)

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
    permission_classes = [user_permission([UserGroups.ADMIN])]
    serializer_class = ProductSerializer
    http_method_names = ['get', 'patch', 'delete']

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


