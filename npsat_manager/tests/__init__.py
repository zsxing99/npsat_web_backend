from django.test import TestCase

import numpy
from scipy import signal

from npsat_manager import mantis

# Create your tests here.

# this was testing a sample Python implementation of Mantis - no longer used
class TestMantis(TestCase):
	def test_mantis(self):
		annual_loadings = mantis.make_annual_loadings([])

		loadings = annual_loadings.T
		del annual_loadings
		unit_response_functions = numpy.ones([loadings.shape[0], loadings.shape[1], loadings.shape[2]],
											 dtype=numpy.float64)
		break1 = int(loadings.shape[1]/2)
		break2 = int(loadings.shape[2]/2)
		print("C1")
		convolved1 = signal.convolve(loadings[:,:break1,:break2], unit_response_functions[:,:break1,:break2])
		print("C2")
		convolved2 = signal.convolve(loadings[:, :break1, break2:], unit_response_functions[:, :break1, break2:])
		print("C3")
		convolved3 = signal.convolve(loadings[:, break1:, :break2], unit_response_functions[:, break1:, :break2],)
		print("C4")
		convolved4 = signal.convolve(loadings[:, break1:, break2:], unit_response_functions[:, break1:, break2:])

