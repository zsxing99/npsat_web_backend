"""
	As opposed to the mantis code that tries to run Mantis in Python (still not fully complete as of this
	writing), this code manages the handoff to a standalone Mantis server that processes requests.

	Because the format of this handoff is still in flux, we'll use a general class and then
	in the future we can subclass it to override certain parts of that behavior while still
	providing the same interface to the rest of the code.

	We'll keep this class separate from the Django code and just make it an interface the Django
	code uses.
"""

import os

from npsat_backend import settings

BASE_FILENAME = os.path.join(settings.MANTIS_FOLDER, "MantisServer")
INPUT_FILENAME = "{}.inp".format(BASE_FILENAME)
LOCK_FILENAME = "{}.inp".format(BASE_FILENAME)
OUTPUT_FILENAME = "{}.inp".format(BASE_FILENAME)


class MantisManager(object):
	def __init__(self):
		self.area_map_id = {
			"npsat_manager.models.CentralValley": 1,
			"npsat_manager.models.SubBasin": 2,
			"npsat_manager.models.CVHMFarm": 3,
			"npsat_manager.models.B118Basin": 4,
			"npsat_manager.models.County": 5,
		}

	def send_command(self, model_run):
		"""

		:param model_run: a npsat_manager.models.model_run object
		:return:
		"""

		area = model_run.area
		modifications = model_run.modifications

		if os.path.exists(OUTPUT_FILENAME):
			raise RuntimeError("Existing output file still in Mantis folder - can't create new run until existing one is finished")

		area_type_id = self.area_map_id[type(area)]  # we key the ids based on the class being used - this is clunky, but efficient
		area_subitem_id = area.mantis_id if area_type_id > 1 else ""  # make it an empty string for central valley
		number_of_records = len(modifications)  # len can be slow with Django, but it'll cache the models for us for later
		with open(INPUT_FILENAME, 'w') as mantis_input:
			mantis_input.write("{} {}").format(area_type_id, area_subitem_id)
			mantis_input.write(str(number_of_records))
			for modification in modifications.objects.all():
				mantis_input.write("{} {}".format(modification.crop.caml_code, modification.proportion))


