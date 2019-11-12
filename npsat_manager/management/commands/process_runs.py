import logging

from django.core.management.base import BaseCommand, CommandError

from npsat_manager import mantis_manager

log = logging.getLogger("npsat_manager.commands.process_runs")


class Command(BaseCommand):
	help = 'Starts the event loop that processes model runs and sends the commands to Mantis'

	def handle(self, *args, **options):
		mantis_manager.main_model_run_loop()
