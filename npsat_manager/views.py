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
from django.db.models import Q


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
class ScenarioViewSet(viewsets.ModelViewSet):
	"""
	scenario name

	Permissions: IsAdminUser | ReadOnly (Admin users can do all operations, others can use HEAD and GET)
	"""
	permission_classes = [IsAdminUser | ReadOnly]
	serializer_class = serializers.ScenarioSerializer
	queryset = models.Scenario.objects.filter(active_in_mantis=True).order_by('name')


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

	Optional params:
		public: true(default), if the user want to include public model
		isBase: true(default), if the user want to include base model
		origin: true(default), if the user want to include self-created model
	These params are additional filter to sift models to return the model list
	"""
	permission_classes = [IsAuthenticated]

	serializer_class = serializers.RunResultSerializer

	def get_queryset(self):
		include_public = self.request.query_params.get("public", "true")
		include_base = self.request.query_params.get("isBase", "true")
		include_origin = self.request.query_params.get("origin", "true")
		# all objects available for user
		# here we are doing a logic like this:
		# as long as the model satisfies any of the true conditions, include it
		# An alternative logic is to exclude the false conditions
		# queryset = models.ModelRun.objects.filter(
		# 	Q(user=self.request.user) | Q(public=True) | Q(isBase=True)
		# )

		query = None
		if include_public == "true":
			query = Q(public=True)
		if include_base == "true":
			query = Q(isBase=True) if not query else query | Q(isBase=True)
		if include_origin == "true":
			query = Q(user=self.request.user) if not query else query | Q(user=self.request.user)

		return models.ModelRun.objects.filter(query) if query else []


class ModificationViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows listing of Modifications

	Permissions: Must be authenticated
	"""
	permission_classes = [IsAuthenticated]

	serializer_class = serializers.ModificationSerializer

	def get_queryset(self):
		return models.Modification.objects.filter(model_run__user=self.request.user).order_by('id')


class ResultPercentileViewSet(viewsets.ModelViewSet):
	"""
	API endpoint for model results
	restricted to only allow GET request

	Permission: same as the model run, must be authenticated
	"""
	permission_classes = [IsAuthenticated]
	http_method_names = ["get"]

	serializer_class = serializers.ResultPercentileSerializer

	def get_queryset(self):
		return models.ResultPercentile.objects\
			.select_related('model')\
			.filter(
				Q(model__user=self.request.user) |
				Q(model__public=True) |
				Q(model__isBase=True)
			)\
			.order_by('id')

