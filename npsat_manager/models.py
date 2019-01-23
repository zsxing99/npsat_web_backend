from django.db import models

# Create your models here.


class Crop(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name

class CropGroup(models.Model):
	"""
		Crop Groups aggregate crops, such as level 1 and 2
		during Delta ET study. Here, groups are arbitrary,
		and so are the levels. Levels let you find all the groups
		in a certain level so that the groups are themselves
		grouped into a useful unit by which you can find
		all the crops in some grouping scheme
	"""
	crops = models.ManyToManyField(to=Crop, related_name="groups")
	level = models.CharField(max_length=255)


class Area(models.Model):
	"""
		Used for the various location models - this will let us have a groupings class
		that can be used for any of the locations
	"""
	npsat_id = models.IntegerField(null=True)
	name = models.CharField(max_length=255)

	class Meta:
		abstract = True

	def __str__(self):
		return self.name


class B118Basin(Area):
	"""

	"""
	b118_id = models.IntegerField()


class County(Area):
	ab_code = models.CharField(max_length=4)
	ansi_code = models.CharField(max_length=3)


#class AreaGroup(models.Model):
"""
	Aggregates different areas so they can be referenced together. Won't work as set up - need
	to either refactor entirely or make this use Generic Relations via a manually made
	middle object. See https://docs.djangoproject.com/en/2.0/ref/contrib/contenttypes/#generic-relations
"""
#areas = models.ManyToManyField(to=Area, related_name="area_groups")
#name = models.CharField(max_length=255)
