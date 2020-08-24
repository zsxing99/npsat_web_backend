from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework import generics
from django.contrib.auth.decorators import login_required

from npsat_manager import serializers
from npsat_manager import models
from npsat_manager.support import tokens  # token code makes sure that all users have tokens - needs to be imported somewhere

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
	"""
	Via https://www.django-rest-framework.org/api-guide/authentication/
	Creates a custom object that returns more than just the auth token when users hit the API endpoint.
	"""
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data,
		                                   context={'request': request})
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		token, created = Token.objects.get_or_create(user=user)
		return Response({
			'token': token.key,
			'user_id': user.pk,
			'username': user.username,
			'is_staff': user.is_staff,
			'is_superuser': user.is_superuser,
			'email': user.email,
		})

class ReadOnly(BasePermission):
	def has_permission(self, request, view):
		return request.method in SAFE_METHODS

# Create your views here.


class CropViewSet(viewsets.ModelViewSet):
	"""
	Crop Names and Codes

	Permissions: IsAdminUser | ReadOnly (Admin users can do all operations, others can use HEAD and GET)
	"""
	permission_classes = [IsAdminUser | ReadOnly]  # Admin users can do any operation, others, can read from the API, but not write

	serializer_class = serializers.CropSerializer
	queryset = models.Crop.objects.order_by('name')


class RegionViewSet(viewsets.ModelViewSet):
	"""
		API endpoint that allows listing of Region

		Permissions: IsAdminUser | ReadOnly (Admin users can do all operations, others can use HEAD and GET)
	"""
	permission_classes = [IsAdminUser | ReadOnly]  # Admin users can do any operation, others, can read from the API, but not write

	serializer_class = serializers.RegionSerializer

	def get_queryset(self):
		queryset = models.Region.objects.filter(active_in_mantis=True).order_by('name')
		region_type = self.request.query_params.get('region_type', None)
		if region_type:
			queryset = queryset.filter(region_type=region_type)
		return queryset


class ModelRunViewSet(viewsets.ModelViewSet):
	"""
	Create, List, and Modify Model Runs

	Test

	Permissions: Must be authenticated
	"""
	permission_classes = [IsAuthenticated]

	serializer_class = serializers.RunResultSerializer

	def get_queryset(self):
		return models.ModelRun.objects.filter(user=self.request.user).order_by('id')


class ModificationViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows listing of Modifications

	Permissions: Must be authenticated
	"""
	permission_classes = [IsAuthenticated]

	serializer_class = serializers.ModificationSerializer

	def get_queryset(self):
		return models.Modification.objects.filter(model_run__user=self.request.user).order_by('id')
