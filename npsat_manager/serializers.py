from rest_framework import serializers

from npsat_manager import models


class CropSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Crop
		fields = ('id', 'name',)


class CountySerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.County
		fields = ('id', 'ab_code', 'ansi_code', 'name', 'mantis_id')


#class ModificationSerializer(serializers.HyperlinkedModelSerializer):
#	crop = CropSerializer(read_only=True)
#	model_run = RunResultSerializer()
#	class Meta:
#		model = models.Modification
#		fields = ('crop', 'proportion', 'model_run')


class ModificationField(serializers.RelatedField):
	def to_representation(self, obj):
		return {
			'id': obj.id,
			'crop': obj.crop.name,
			'crop_id': obj.crop.id,
			'model_run': obj.model_run.id,
			'proportion': obj.proportion,
		}

	def to_internal_value(self, data):
		try:
			try:
				if 'id' in data:
					return models.Modification.objects.get(id=data['id'])
			except ValueError:
				raise serializers.ValidationError(
					'id must be an integer.'
				)
		except models.Modification.DoesNotExist:
			raise serializers.ValidationError(
				'Modification does not exist.'
			)


class RunResultSerializer(serializers.ModelSerializer):
	modifications = serializers.RelatedField(many=True, queryset=models.Modification.objects.all())
	county = CountySerializer(read_only=True)

	class Meta:
		model = models.ModelRun
		fields = ('id', 'county', 'modifications', 'result_values', 'date_run', 'complete', 'status_message')

	def validate(self, data):
		print(data)
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
