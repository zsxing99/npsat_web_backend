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
		fields = ('id', 'external_id', 'name', 'mantis_id')


class ModificationSerializer(serializers.ModelSerializer):
	# crop = CropSerializer(read_only=True)
	#model_run = RunResultSerializer()

	class Meta:
		model = models.Modification
		fields = ('crop', 'proportion', 'land_area_proportion', 'model_run')

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


class RunResultSerializer(serializers.ModelSerializer):
	modifications = ModificationSerializer(many=True, allow_null=True, read_only=True) # for now, we're explicity blocking nested writes
	regions = NestedRegionSerializer(many=True, allow_null=True, read_only=True) # for now, we're explicity blocking nested writes
	# we might enable nested writes later, in which case, remove the read_only flag.

	# don't put the county serializer here or else we'll get the county geometries for every run result read (do not want)
	# county = CountySerializer(read_only=True)

	class Meta:
		model = models.ModelRun
		fields = ('id', 'user', 'name', 'description', 'regions', 'modifications', 'result_values', 'unsaturated_zone_travel_time',
		          'date_submitted', 'date_completed', 'ready', 'complete', 'running', 'status_message')
		depth = 0  # should mean that modifications get included in the initial request

	def validate(self, data):
		return data

	#def create(self, validated_data):
	#	print(validated_data)
	#	modifications = validated_data.pop('modifications')

		# get the county object - this will need to change when we expand it to handle other areas
	#	county_id = validated_data.pop('county')
	#	county = models.County.objects.get(ab_code=county_id)

		# create the base model run
	#	model_run = models.ModelRun.objects.create(county=county)
	#	model_run.save()
	#	for modification in modifications:
	#		crop = models.Crop.objects.get(name=modification['name'])
	#		mod_object = models.Modification.objects.create(model_run=model_run, crop=crop, proportion=modification.proportion)
	#		mod_object.save()


