from npsat_manager import models


def load_crops():
	"""
		At some point this should probably just read a CSV or
		something like that
	:return:
	"""

	crops = ["Corn", "Grapes", "Alfalfa", "Wheat", "Barley", "Rye"]

	for crop in crops:
		models.Crop(name=crop).save()

