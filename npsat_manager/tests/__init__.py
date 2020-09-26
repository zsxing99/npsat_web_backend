from django.test import TestCase, RequestFactory

from npsat_manager import models
from npsat_manager import views
from django.contrib.auth.models import User

# Create your tests here.
class TestViewSet(TestCase):
	def setUp(self) -> None:
		self.factory = RequestFactory()
		# create a user and some models
		self.test_man = User.objects.create(username="testMan", password="onlyForTest")
		self.test_women = User.objects.create(username="testWomen", password="onlyForTest")
		scenario = models.Scenario.objects.create(name="testScenario")
		models.ModelRun.objects.create(user=self.test_man, public=True, isBase=False, scenario=scenario)
		models.ModelRun.objects.create(user=self.test_man, public=False, isBase=False, scenario=scenario)
		models.ModelRun.objects.create(user=self.test_man, public=False, isBase=True, scenario=scenario)
		models.ModelRun.objects.create(user=self.test_women, public=False, isBase=False, scenario=scenario)
		models.ModelRun.objects.create(user=self.test_women, public=True, isBase=False, scenario=scenario)

	def test_model_run_view_set_get(self):
		# case 1 all available models for test man (3 self created and 1 public from others)
		request = self.factory.get('/model_run/')
		request.user = self.test_man
		response = views.ModelRunViewSet.as_view({'get': 'list'})(request)
		self.assertEqual(response.data["count"], 4)

		# case 2 all available models for test women (2 self created and 1 public and 1 base)
		request = self.factory.get('/model_run/')
		request.user = self.test_women
		response = views.ModelRunViewSet.as_view({'get': 'list'})(request)
		self.assertEqual(response.data["count"], 4)

