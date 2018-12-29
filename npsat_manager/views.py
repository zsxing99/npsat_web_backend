from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from npsat_manager.serializers import CropSerializer
from npsat_manager import models


# Create your views here.

class CropViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows viewing of CTD Data
	"""
	serializer_class = CropSerializer
	queryset = models.Crop.objects.order_by('name')
