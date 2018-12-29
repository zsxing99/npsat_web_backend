from django.shortcuts import render

from rest_framework import viewsets

from npsat_manager.serializers import CropSerializer
from npsat_manager import models

# Create your views here.


class CropViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows viewing of CTD Data
	"""
	serializer_class = CropSerializer
	queryset = models.Crop.objects.order_by('-name')
