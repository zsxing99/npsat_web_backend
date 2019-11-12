Client needs to send 3 requests:

1. request that creates the ModelRun and attaches it to the user. Should POST
to the model_run endpoint with a user ID in the POST data. Response returns model_run object
that has the new `ModelRun` ID
2. Submit post request to attach modifications to the model_run
3. Submit a modification request to change model_run attribute `ready` to True. Only once this
is marked True will the server process the run
4. Occasionally poll for results can get the model_run object - once `complete` is True,
then the `result_values` field should be populated with a timeseries.

See sample_client.py for a demonstration of the implementation