import numpy
import logging
import sys

import arcpy

from npsat_backend import settings

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger("npsat_manager.mantis")

earliest_data_year = 1945
latest_data_year = 2050
min_year = earliest_data_year  # datetime.datetime.now().year
time_range = 105
max_year = min_year + time_range



"""
	Make a script that rewrites the URFs into a multidimensional raster
"""

"""
	Given user input loading values, reclassify land use rasters to use those new loading proportions.
	For values not given, use the value "1" - maybe we could use a raster that is constant 1s, then
	only adjust specific masks - not sure.

	Do this for each time range.

	Multiply these times the NGw rasters to get the modified scenario rasters. We'd also need to figure
	out some way to interpolate between the defined years for each. It'd be good to plan a route
	that gets us the end result of a reduced NGw/year band. This is flexible to adapt to be the same
	as Giorgos's code though.

	Then we need to convolute. This is where, for each year, we add the loading to every future year
	based on the current year's (reduced) value * the unit response function for the *distance* from the
	current year. When we're done, we sum that whole year's raster.

	If the URFs are just a multidimensional raster too, then we can multiply this year's reduced
	loading raster times all of the bands in the URF raster (from 0 until the end of period is
	reached - we can use a slice for that). Then we can just sum this stack with the sliced
	stack representing all years (by year).

	Then, when we're done, we just sum the raster band representing each year for our value.
"""

def make_weight_raster(land_use, modifications):
	"""
		Given a land use raster and a set of weights, applies the weights to each land use type
		then sets everything else to 1 so that the raster can be used as a multiplier later
	:param land_use: path to a land use raster on disk
	:param modifications: an iterable of npsat_manager.models.Modification objects
	:return:
	"""
	land_use_array = arcpy.RasterToNumPyArray(arcpy.Raster(land_use), )
	land_use_array += 10000  # offset everything by 10000 so we can identify everything that's still a default later
	for modification in modifications:
		land_use_array[land_use_array == modification.crop.caml_code] = modification.reduction

	land_use_array[land_use_array >= 10000] = 1

	return land_use_array


def run(spatial_subset="Tulare"):  # make sure to only run it for Tulare, which we have the URFs for here
									# need to subset the other rasters to that area
	pass


def create_ranges_nd(start, stop, N, endpoint=True):
	"""
		Via https://stackoverflow.com/a/46694364 - for making in between matrices

		Basically, given a 2D array as start and a 2D array as stop, it will return
		a new 3D array (with N values in 3rd dimension) that interpolates between
		start and stop.

		Think of it as taking two bands of a raster and making them the first and last.
		Then, this function adds N-2 bands in between them where the cells are linearly
		interpolated values between the start and stop band cell values. That's what
		we're using this for.

	:param start:
	:param stop:
	:param N:
	:param endpoint:
	:return:
	"""
	if endpoint:
		divisor = N-1
	else:
		divisor = N
	steps = (1.0/divisor) * (stop - start)
	return start[...,None] + steps[...,None]*numpy.arange(N)


def make_annual_loadings(modifications, years=settings.NgwRasters.keys()):

	# First make the loadings for just the years we have precalculated (1945, 1960, etc)

	print("Building Annual Loadings")
	loadings = {}
	for year in years:
		print(year)
		base_loading_matrix = arcpy.RasterToNumPyArray(arcpy.Raster(settings.NgwRasters[year]))
		if year >= settings.ChangeYear:  # if this year is after our reductions are supposed to be made
			weight_matrix = make_weight_raster(settings.LandUserRasters[year], modifications=modifications)
			loadings[year] = weight_matrix * base_loading_matrix
		else:  # otherwise, use the straight Ngw values - no changes have been made since they're in the past
			loadings[year] = base_loading_matrix

	# Now that we have the values for the base years, we want to interpolate between them to make ndarrays for each year

	print("Interpolating between years")
	sorted_years = sorted(years)
	all_years_data = None
	for i, year in enumerate(sorted_years):
		print(year)
		if year == sorted_years[-1]:  # if it's the last year, we have special behavior
			break

		next_data_year = sorted_years[i+1]
		interval_size = next_data_year - year
		all_years_in_range = create_ranges_nd(loadings[year], loadings[next_data_year], interval_size)
		if all_years_data is None:
			all_years_data = all_years_in_range
		else:
			all_years_data = numpy.concatenate([all_years_data, all_years_in_range], -1)  # stack them on the last axis now

	return all_years_data

if __name__ == "__main__":
	annual_loadings = make_annual_loadings([])
	print(annual_loadings.shape)