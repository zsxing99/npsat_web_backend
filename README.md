# npsat_web
Web Interface for the NPSAT tool

See Confluence for internal notes on how we deployed this


## Model Runs
This backend code has a slightly convoluted process for handling runs, but it makes sense based
on the other design constraints. The main Django code accepts parameters for a new run over the 
ModelRun API interface. It logs these parameters to the database for a ModelRun.

A django management command `process_runs` must be running in the background - it is set up this
way since it needs its own event loop to be able to manage a queue and send commands to the Mantis
server and load results. It will pull new runs from the database and send them to Mantis,
then load results in the database when they come back. ModelRun.running and ModelRun.complete
will be set appropriately to reflect the status of a ModelRun. An API endpoint can provide
this status so the frontend can query whether results are available, then query for results
when they are ready (or maybe if it queries for status and status is "complete" it gets the
results back too to save additional querying)
