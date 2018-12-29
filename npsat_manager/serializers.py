from rest_framework import serializers

from npsat_manager import models

class CropSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Crop
		fields = ('name')