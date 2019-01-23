from rest_framework import serializers

from npsat_manager import models


class CropSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Crop
		fields = ('id', 'name',)


class CountySerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.County
		fields = ('id', 'ab_code', 'ansi_code', 'name','npsat_id')
