import csv
import os

from npsat_backend import settings

from npsat_manager import models


def load_all():
	load_crops()
	load_counties()


def load_crops():
	"""
		At some point this should probably just read a CSV or
		something like that
	:return:
	"""

	crops = ["Corn", "Grapes", "Alfalfa", "Wheat", "Barley", "Rye"]

	for crop in crops:
		models.Crop(name=crop).save()


def load_counties():
	"""
		:return:
	"""

	with open(os.path.join(settings.BASE_DIR, "npsat_manager", "data", "counties.csv")) as county_file:
		counties = csv.DictReader(county_file)
		for county in counties:
			models.County(name=county['name'], ab_code=county['abcode'], ansi_code=county['ansi']).save()

