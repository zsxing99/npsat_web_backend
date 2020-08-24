from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework import serializers

from npsat_manager import models


class CropSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Crop
		fields = ('id', 'name', 'caml_code')


class RegionSerializer(serializers.ModelSerializer):
	geometry = serializers.JSONField(read_only=True, binary=False)
	class Meta:
		model = models.Region
		fields = ('id', 'external_id', 'name', 'mantis_id', 'geometry', 'region_type')


class NestedRegionSerializer(serializers.ModelSerializer):  # for use when nested in the model runs to remove geometry
	class Meta:
		model = models.Region
		fields = ('id', 'external_id', 'name', 'mantis_id', 'region_type')
		# set id/name/region_type values for POST method
		extra_kwargs = {
			"id": {
				"read_only": False,
				"required": False,
			},
			"name": {
				"required": False,
			},
			"region_type": {
				"required": False
			}
		}


class ModificationSerializer(serializers.ModelSerializer):
	# crop = CropSerializer(read_only=True)
	#model_run = RunResultSerializer()

	class Meta:
		model = models.Modification
		fields = ('crop', 'proportion', 'model_run')

	def validate(self, data):

		# check that the user making this modification actually has permission to attach it to the specified model run.
		request = self.context.get("request")
		if request and hasattr(request, "user"):
			user = request.user
		else:
			raise PermissionDenied("No User attached to this request - can't modify")

		print(user)
		model_run = data.get('model_run')
		print(model_run)
		print(model_run.user_id)

		if user != model_run.user:
			raise PermissionDenied("You don't have permission to attach modifications to this model run")

		return data


class NestedModificationSerializer(serializers.ModelSerializer):

	class Meta:
		model = models.Modification
		fields = ('id', 'crop', 'proportion')


class RunResultSerializer(serializers.ModelSerializer):
	modifications = NestedModificationSerializer(many=True, allow_null=True, partial=True)
	regions = NestedRegionSerializer(many=True, allow_null=True, partial=True, read_only=False)

	class Meta:
		model = models.ModelRun
		fields = ('id', 'user', 'name', 'description', 'regions', 'modifications', 'result_values', 'unsaturated_zone_travel_time',
		          'date_submitted', 'date_completed', 'ready', 'complete', 'running', 'status_message', 'n_years', 'water_content',
				  'reduction_year', 'scenario_name')
		depth = 0  # should mean that modifications get included in the initial request

	def validate(self, data):
		return data

	def create(self, validated_data):
		regions_data = validated_data.pop('regions')
		modifications_data = validated_data.pop('modifications')

		model_run = models.ModelRun.objects.create(**validated_data)
		for modification in modifications_data:
			models.Modification.objects.create(model_run=model_run, **modification)

		for region in regions_data:
			model_run.regions.add(models.Region.objects.get(id=region['id']))

		return model_run