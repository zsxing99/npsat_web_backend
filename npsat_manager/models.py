import traceback
import logging
import asyncio

import django
from django.db import models
from django.core.validators import int_list_validator
from django.contrib.auth.models import User

import arrow

from npsat_backend import settings
# Create your models here.

log = logging.getLogger("npsat.manager")

mantis_area_map_id = {
			"npsat_manager.models.CentralValley": 1,
			"npsat_manager.models.SubBasin": 2,
			"npsat_manager.models.CVHMFarm": 3,
			"npsat_manager.models.B118Basin": 4,
			"npsat_manager.models.County": 5,
}


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
	ready = models.BooleanField(default=False, null=False)  # marked after the web interface adds all modifications
	running = models.BooleanField(default=False, null=False)  # marked while in processing
	complete = models.BooleanField(default=False, null=False)  # tracks if the model has actually been run for this result yet
	status_message = models.CharField(max_length=2048, default="", null=True, blank=True)  # for status info or error messages
	result_values = models.CharField(validators=[int_list_validator], max_length=4096, default="", null=True, blank=True)
	date_run = models.DateTimeField(default=django.utils.timezone.now, null=True)
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="model_runs")

	# when null, run whole central valley
	county = models.ForeignKey(County, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="model_runs")
	# modifications

	def load_result(self, values):
		self.result_values = ",".join([str(item) for item in values])
		self.date_run = arrow.utcnow().datetime

	def run(self):
		"""
			Runs Mantis and sets the status codes. Saves automatically at the end
		:return:
		"""
		try:
			# TODO: Fix below
			results = None #mantis.run_mantis(self.modifications.all())
			self.load_result(values=results)
			self.complete = True
			self.status_message = "Successfully run"
		except:
			log.error("Failed to run Mantis. Error was: {}".format(traceback.format_exc()))
			self.complete = True
			self.status_message = "Model run failed. This error has been reported."

		self.save()


class Modification(models.Model):
	class Meta:
		unique_together = ['model_run', 'crop']

	crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, related_name="modifications")
	proportion = models.FloatField()  # the amount, relative to 2020 of nitrogen applied on these crops - 0 to 1

	model_run = models.ForeignKey(ModelRun, null=True, blank=True, on_delete=models.CASCADE, related_name="modifications")


class MantisServer(models.Model):
	"""
		We can configure a server pool by instantiating different versions of this model. On startup, a function willl
		trigger each instance to determine if it is online and available, at which point when we go to send out tasks,
		it will be available for use.
	"""

	host = models.CharField(max_length=255)
	port = models.PositiveSmallIntegerField(default=1234)
	online = models.BooleanField(default=False)

	async def get_status(self):
		stream_reader, stream_writer = asyncio.open_connection(self.host, self.port)
		stream_writer.write(settings.MANTIS_STATUS_MESSAGE)
		await stream_writer.drain()

		response = stream_reader.read()  # waits for an "EOF"
		log.debug("Mantis server at {}:{} responded {}".format(self.host, self.port, response))
		if response == settings.MANTIS_STATUS_RESPONSE:
			self.online = True
		else:
			self.online = False
		self.save()

	def startup(self):
		self.get_status()  # saves the object once it determines if the server is online

	async def send_command(self, model_run: ModelRun):
		"""
			Sends commands to MantisServer and loads results back
		:param model_run:
		:return:
		"""
		area = model_run.area
		modifications = model_run.modifications

		area_type_id = mantis_area_map_id[type(area)]  # we key the ids based on the class being used - this is clunky, but efficient
		area_subitem_id = area.mantis_id if area_type_id > 1 else ""  # make it an empty string for central valley
		number_of_records = len(modifications)  # len can be slow with Django, but it'll cache the models for us for later

		mantis_reader, mantis_writer = asyncio.open_connection(self.host, self.port)

		# sent the command to the server
		mantis_writer.write("{} {}").format(area_type_id, area_subitem_id)
		mantis_writer.write(" {} {}".format(str(number_of_records), settings.ChangeYear))
		for modification in modifications.objects.all():
			mantis_writer.write(" {} {}".format(modification.crop.caml_code, modification.proportion))
		mantis_writer.write("\n")

		await mantis_writer.drain()  # make sure the full command is sent before proceeding with this function

		results = mantis_reader.read()  # basically, wait for the EOF signal
		model_run.result_values = results
		model_run.complete = True
		model_run.running = False
		model_run.save()
