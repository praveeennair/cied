from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

class AdminHomeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response('<h1> Home </h1>')
