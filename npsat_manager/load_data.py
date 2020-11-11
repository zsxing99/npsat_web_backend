import csv
import os
import json

from npsat_backend import settings

from npsat_manager import models


def load_all():
	load_crops()
	load_regions()


def load_regions():
	load_counties()
	load_farms()
	load_central_valley()
	load_basins()
	load_townships()


def load_crops():
	"""
		At some point this should probably just read a CSV or
		something like that
	:return:
	"""

	crops = [("All Other Crops", 0), ("Corn", 606), ("Grapes", 2200)]

	for crop in crops:
		models.Crop(name=crop[0], caml_code=crop[1]).save()


def load_counties():
	"""
		:return:
	"""

	county_file = os.path.join(settings.BASE_DIR, "npsat_manager", "data", "california-counties-1.0.0", "geojson", "california_counties_simplified_0005.geojson")
	load_spec_regions(county_file, (("name", "name"), ("abcode", "external_id")), region_type="County")  #, ("ansi", "ansi_code")))

	enable_default_counties(all=True)  # all is True just for testing - we'll set this to False later


def load_farms():
	"""
	:return:
	"""

	field_map = (
		('dwr_sbrgns', 'external_id'),
		('ShortName', 'name'),
	)
	farm_file = os.path.join(settings.BASE_DIR, "npsat_manager", "data", "CVHM-farm", "geojson", "CVHM_farms_cleaned.geojson")
	load_spec_regions(farm_file, field_map, region_type="CVHMFarm")


def load_central_valley():
	central_valley_file = os.path.join(settings.BASE_DIR, "npsat_manager", "data", "central_valley.geojson")
	load_spec_regions(central_valley_file, (("name", "name"), ("Id", "external_id")), region_type="Central Valley")


def load_basins():
	basin_file = os.path.join(settings.BASE_DIR, "npsat_manager", "data", "Basin", "geojson", "basin.geojson")
	load_spec_regions(basin_file, (("CVHM_Basin", "name"), ("Basin_ID", "external_id")), region_type="Basin")


def load_townships():
	basin_file = os.path.join(settings.BASE_DIR, "npsat_manager", "data", "townships", "geojson", "townships.geojson")
	load_spec_regions(basin_file, (("TOWNSHIP", "name"), ("TOWNSHIP", "external_id")), region_type="Townships")


def load_spec_regions(json_file, field_map, region_type):
	"""
		Given a geojson file, loads each record as a county instance, assigning data
		to fields by the field map. The geojson file isn't a standard file, but instead just
		the individual records for each feature, with no enclosing array, one per line (as saved by
		QGIS in a specific format, with newline delimited)

		Warning: It loads the *whole* geojson record in as geometry, even attributes that
		aren't in the field map, so all attributes will be sent to the client. If you don't
		want this or want a leaner GeoJSON, strip unnecessary information out before loading
	:param json_file: newline delimited GeoJSON file (QGIS can export this) of the regions
	:param field_map: iterable of two-tuples. First value is the field in the datasets,
					and the second is the field here in npsat_manager (think "from", "to")
	:param model_area: The model area instance to attach these regions to
	:return:
	"""

	with open(json_file, 'r') as input_data:
		geojson = input_data.readlines()

	for record in geojson:
		# make a Python version of the JSON record
		python_data = json.loads(record)
		region = models.Region()  # make a new region object
		region.geometry = record  # save the whole JSON record as the geometry we'll send to the browser in the future

		for fm in field_map:  # apply all the attributes to the region based on the field map
			value = python_data["properties"][fm[0]]
			if hasattr(region, fm[1]):  # we need to check if that attribute exists first
				setattr(region, fm[1], value)  # if it does, set it on the region object
			setattr(region, 'region_type', region_type)

		region.save()  # save it with the new attributes


def enable_default_counties(enable_counties=("Tulare", ), all=False):
	"""
		By default, we consider counties inactive so they don't show in the list if we can't use them.

		If all=True, ignores enable_counties and just enables all counties. When False, only enables counties whose
		names are in the list
	:return:
	"""
	if all:
		counties = []
		for county in models.Region.objects.all():
			county.active_in_mantis = True
			counties.append(county)
		models.Region.objects.bulk_update(counties, ["active_in_mantis"])
	else:
		for county in enable_counties:
			update_county = models.Region.objects.get(name=county)
			update_county.active_in_mantis = True
			update_county.save()


def enable_region_dev_data(enable_regions=("Central Valley", ), all=False):
	"""
		For dev purpose, enable all regions

		If all=True, ignores enable_counties and just enables all counties. When False, only enables counties whose
		names are in the list
	:return:
	"""
	if all:
		regions = []
		for region in models.Region.objects.all():
			region.active_in_mantis = True
			regions.append(region)
		models.Region.objects.bulk_update(regions, ["active_in_mantis"])
	else:
		for county in enable_regions:
			update_region = models.Region.objects.get(name=county)
			update_region.active_in_mantis = True
			update_region.save()


def enable_scenario_dev_data():
	models.Scenario(name='CVHM_70_03', active_in_mantis=True).save()
	models.Scenario(name='C2VSIM_99_09', active_in_mantis=True).save()

