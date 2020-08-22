import traceback
import logging
import asyncio
import socket
import json

import django
from django.db import models
from django.core.validators import int_list_validator
from django.contrib.auth.models import User

from asgiref.sync import sync_to_async

import arrow

from npsat_backend import settings
# Create your models here.

log = logging.getLogger("npsat.manager")

mantis_area_map_id = {
			"CentralValley": 1,
			"SubBasin": 2,
			"CVHMFarm": 5,
			"B118Basin": 4,
			"County": 3,
}


class PercentileAggregate(models.Aggregate):
	function = 'PERCENTILE_CONT'
	name = 'pct'
	output = models.FloatField()
	template = 'percentile_cont(0.5) WITHIN GROUP (ORDER BY year asc)'


class SimpleJSONField(models.TextField):
	"""
		converts dicts to JSON strings on save and converts JSON to dicts
		on load
	"""

	def get_prep_value(self, value):
		if type(value) in (str, bytes):
			return value

		return json.dumps(value)

	def from_db_value(self, value, expression, connection):
		return json.loads(value)


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


class Region(models.Model):
	"""
		Used for the various location models - this will let us have a groupings class
		that can be used for any of the locations
	"""

	mantis_id = models.IntegerField(null=True)
	name = models.CharField(max_length=255)
	active_in_mantis = models.BooleanField(default=False)  # Is this region actually ready to be selected?
	geometry = SimpleJSONField(null=True, blank=True)  #
	external_id = models.CharField(null=True, max_length=255, blank=True)
	region_type = models.CharField(max_length=25)  # is it a county, a B118 Basin, etc? we'll need to have some kind of code for this

	def __str__(self):
		return self.name


#class AreaGroup(models.Model):
"""
	Aggregates different areas so they can be referenced together. Won't work as set up - need
	to either refactor entirely or make this use Generic Relations via a manually made
	middle object. See https://docs.djangoproject.com/en/2.0/ref/contrib/contenttypes/#generic-relations
"""
#areas = models.ManyToManyField(to=Area, related_name="area_groups")
#name = models.CharField(max_length=255)


# We should create the following API endpoint to get the percentiles
#/api/percentile/
#{
#	percentiles = [5,15,85,95],
#	model_run = 27
#}

class ModelRun(models.Model):
	"""
		The central object for configuring an individual run of the model - is related to modification objects from the
		modification side.
	"""
	name = models.CharField(max_length=255, null=False, blank=False)
	description = models.TextField(null=True, blank=True)

	ready = models.BooleanField(default=False, null=False)  # marked after the web interface adds all modifications
	running = models.BooleanField(default=False, null=False)  # marked while in processing
	complete = models.BooleanField(default=False, null=False)  # tracks if the model has actually been run for this result yet
	status_message = models.CharField(max_length=2048, default="", null=True, blank=True)  # for status info or error messages
	result_values = models.TextField(validators=[int_list_validator], default="", null=True, blank=True)
	date_submitted = models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)
	date_completed = models.DateTimeField(null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="model_runs")

	# global model parameters
	unsaturated_zone_travel_time = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)

	# model will be run on these regions
	regions = models.ManyToManyField(Region, related_name="model_runs")

	# other model specs
	n_years = models.IntegerField(default=100, blank=True)
	reduction_year = models.IntegerField(default=2020, blank=True)
	water_content = models.DecimalField(max_digits=5, decimal_places=4)
	scenario_name = models.CharField(max_length=255)

	# modifications - backward relationship

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
			results = None  # mantis.run_mantis(self.modifications.all())
			self.load_result(values=results)
			self.complete = True
			self.status_message = "Successfully run"
		except:
			log.error("Failed to run Mantis. Error was: {}".format(traceback.format_exc()))
			self.complete = True
			self.status_message = "Model run failed. This error has been reported."

		self.save()

	def get_results_percentile(self, percentile):
		results_by_year = self.results.aggregate(PercentileAggregate('loading', percentile=percentile, year_field='year'))


class ResultLoading(models.Model):

	model_run = models.ForeignKey(ModelRun, on_delete=models.CASCADE, related_name="results")
	loading = models.FloatField(null=False, blank=False)
	year = models.SmallIntegerField()  # this will be inferred from the order of values coming out of Mantis
	well = models.IntegerField()  # this is just an ID assigned to each stream of values in order coming from Mantis.
									# each well with the same value is *not* the same between model runs, but allows
									# us to group within a model run


class Modification(models.Model):
	class Meta:
		unique_together = ['model_run', 'crop']

	crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, related_name="modifications")
	proportion = models.DecimalField(max_digits=5, decimal_places=4)  # the amount, relative to 2020 of nitrogen applied on these crops - 0 to 1
	# land_area_proportion = models.DecimalField(max_digits=5, decimal_places=4)
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
		pass
		#self.get_status()  # saves the object once it determines if the server is online

	def send_command(self, model_run: ModelRun, scenario="CVHM_95_99"):
		"""
			Sends commands to MantisServer and loads results back
		:param model_run:
		:return:
		"""
		model_run.running = True
		model_run.save()
		modifications = model_run.modifications

		number_of_records = len(modifications.all())  # len can be slow with Django, but it'll cache the models for us for later

		log.debug("Connecting to server to send command")
		try:
			self._non_async_send(model_run, number_of_records, modifications)
		except:
			# on any exception, reset the state of this model run so it will be picked up again later
			model_run.running = False
			model_run.complete = False
			model_run.save()
			raise

	def _non_async_send(self, model_run, number_of_records, modifications):
		# sanity check: model_run must be attached with at least one region
		if len(model_run.regions.all()) < 1:
			return
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.host, self.port))
		# mantis_reader, mantis_writer = asyncio.open_connection(server.host, server.port)
		# log.debug("Connected successfully")

		region_type = model_run.regions.all()[0].region_type
		# sent the command to the server
		# detailed input refers to https://github.com/giorgk/Mantis#format-of-input-message
		command_string = "{} {} {} {}".format(model_run.n_years, model_run.reduction_year, model_run.water_content, model_run.scenario_name)
		command_string += " {}".format(mantis_area_map_id[region_type])
		command_string += " {}".format(len(model_run.regions.all()))
		if mantis_area_map_id[region_type] != 1:
			for region in model_run.regions.all():
				command_string += " {}".format(region.mantis_id)
		command_string += " {}".format(number_of_records)
		for modification in modifications.all():
			command_string += " {} {}".format(modification.crop.caml_code, 1 - modification.proportion)
		command_string += ' ENDofMSG\n'
		log.info("Command String is: {}".format(command_string))
		s.send(command_string.encode('utf-8'))

		# s.flush()
		# mantis_writer.drain()  # make sure the full command is sent before proceeding with this function

		results = s.recv(9999999)  # basically, wait for Mantis to close the connection
		model_run.result_values = str(results)
		model_run.complete = True
		model_run.running = False
		model_run.date_completed = arrow.utcnow().datetime
		model_run.save()

		log.info("Results saved")