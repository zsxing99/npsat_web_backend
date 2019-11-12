"""
	As opposed to the mantis code that tries to run Mantis in Python (still not fully complete as of this
	writing), this code manages the handoff to a standalone Mantis server that processes requests.
"""

import asyncio
import logging

from npsat_manager import models

log = logging.getLogger("npsat.manager.mantis_manager")

LOAD_SLEEP = 1


async def load_runs_to_queue(q: asyncio.Queue) -> None:
	while True:
		new_runs = models.ModelRun.objects.filter(ready=True, running=False, complete=False)  # get runs that aren't complete
		for run in new_runs:
			run.running = True  # TODO: ON STARTUP, all model.running should be set to False
			run.save()
			q.put_nowait(run)
			log.info("Added run {} to queue".format(run.pk))

		await asyncio.sleep(LOAD_SLEEP)  # yield time to workers


async def worker_func(server, q: asyncio.Queue) -> None:
	while True:
		model_run = await q.get()  # basically, this function will sleep until there's something to do
		log.info("Processing run {} on worker {}".format(model_run.pk, server.host))
		server.send_command(model_run)
		q.task_done()


async def main_model_run_loop():

	# we're assuming we're starting now, so set ModelRuns to not running if they're not complete
	# this helps if the server shut down while running an analysis and makes sure it gets run when it starts up next.
	all_incomplete_runs = models.ModelRun.objects.filter(complete=False)
	for run in all_incomplete_runs:
		run.running = False
		run.save()

	# Now figure out which servers are online - go through the MantisServer object's startup sequence
	all_mantis_servers = models.MantisServer.objects.all()
	for server in all_mantis_servers:
		server.startup()

	# Now we can actually begin the work of passing information
	# start up a new queue
	q = asyncio.Queue()

	# run_loader checks for new ModelRuns in the DB and throws them into the queue that the servers pull from.
	# we could do this without a queue and just have the servers check the DB, but this results in less DB traffic, I think
	run_loader = asyncio.create_task(load_runs_to_queue(q))

	# get the online servers only
	mantis_servers = models.MantisServer.objects.filter(online=True)
	# initialize a set of workers using those servers
	workers = [asyncio.create_task(worker_func(server, q)) for server in mantis_servers]

	await asyncio.gather(run_loader)
	await q.join()  # Implicitly awaits consumers, too
	for worker in workers:
		worker.cancel()
