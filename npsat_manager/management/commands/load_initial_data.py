import logging

from django.core.management.base import BaseCommand

from npsat_manager import load_data

log = logging.getLogger("npsat_manager.commands.process_runs")

class Command(BaseCommand):
	help = 'Starts the event loop that processes model runs and sends the commands to Mantis'

	def handle(self, *args, **options):
		load_data.load_all()