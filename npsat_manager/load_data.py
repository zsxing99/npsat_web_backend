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

	crops = [("Corn", 606), ("Grapes", 2200)]

	for crop in crops:
		models.Crop(name=crop[0], caml_code=crop[1]).save()


def load_counties():
	"""
		:return:
	"""

	with open(os.path.join(settings.BASE_DIR, "npsat_manager", "data", "counties.csv")) as county_file:
		counties = csv.DictReader(county_file)
		for county in counties:
			models.County(name=county['name'], ab_code=county['abcode'], ansi_code=county['ansi']).save()

	enable_default_counties()


def enable_default_counties(enable_counties=("Tulare",)):
	"""
		By default, we consider counties inactive so they don't show in the list if we can't use them.
	:return:
	"""

	for county in enable_counties:
		update_county = models.County.objects.get(name=county)
		update_county.active_in_npsat = True
		update_county.save()