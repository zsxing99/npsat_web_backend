import traceback
import logging

from django.db import models
from django.core.validators import int_list_validator
from django.contrib.auth.models import User

import arrow
# Create your models here.

from npsat_manager import mantis

log = logging.getLogger("npsat.manager")


class Crop(models.Model):
	name = models.CharField(max_length=255)
	caml_code = models.PositiveSmallIntegerField()

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
	mantis_id = models.IntegerField(null=True)
	name = models.CharField(max_length=255)
	active_in_mantis = models.BooleanField(default=False)  # Is this region actually ready to be selected?

	class Meta:
		abstract = True

	def __str__(self):
		return self.name

class SubBasin(Area):
	subbasin_id = models.IntegerField()

class CVHMFarm(Area):
	farm_id = models.IntegerField()


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


class ModelRun(models.Model):
	complete = models.BooleanField(default=False)  # tracks if the model has actually been run for this result yet
	status_message = models.CharField(max_length=2048)  # for status info or error messages
	result_values = models.CharField(validators=[int_list_validator], max_length=4096)
	date_run = models.DateTimeField()
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="model_runs")
	# modifications
	area = models.ForeignKey(Area, on_delete=models.DO_NOTHING, related_name="model_runs")

	def load_result(self, values):
		self.result_values = ",".join([str(item) for item in values])
		self.date_run = arrow.utcnow().datetime

	def run(self):
		"""
			Runs Mantis and sets the status codes. Saves automatically at the end
		:return:
		"""
		try:
			results = mantis.run_mantis(self.modifications.all())
			self.load_result(values=results)
			self.complete = True
			self.status_message = "Successfully run"
		except:
			log.error("Failed to run Mantis. Error was: {}".format(traceback.format_exc()))
			self.complete = True
			self.status_message = "Model run failed. This error has been reported."

		self.save()


class Modification(models.Model):
	# run
	crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, related_name="modifications")
	proportion = models.FloatField()  # the amount, relative to 2020 of nitrogen applied on these crops - 0 to 1

	model_run = models.ForeignKey(ModelRun, on_delete=models.DO_NOTHING)


