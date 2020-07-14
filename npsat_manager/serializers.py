from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework import serializers

from npsat_manager import models


class CropSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Crop
		fields = ('id', 'name', 'caml_code')


class CountySerializer(serializers.ModelSerializer):
	geometry = serializers.JSONField(read_only=True, binary=False)
	class Meta:
		model = models.County
		fields = ('id', 'ab_code', 'ansi_code', 'name', 'mantis_id', 'geometry')


class RunResultSerializer(serializers.ModelSerializer):
	#modifications = serializers.RelatedField(many=True, queryset=models.Modification.objects.all())
	#county = CountySerializer(read_only=True)

	class Meta:
		model = models.ModelRun
		fields = ('id', 'user', 'name', 'description', 'county', 'modifications', 'result_values', 'unsaturated_zone_travel_time',
		          'date_submitted', 'date_completed', 'ready', 'complete', 'running', 'status_message')

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


class ModificationSerializer(serializers.ModelSerializer):
	#crop = CropSerializer(read_only=True)
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
