# prefect-exporter

## Configuration

Environment variables:

* `PREFECT_API_KEY`

## Metrics schema

### `flow_run_last_state_ts`

Timestamp of last flow run for each flow, project and state combination.

Labels:

* `project` - project name
* `flow` - flow name
* `state` - "Success"/"Failed"
* `param__{xxx}` - Parameters from flow run parameters if set

Value: Timestamp of last observed flow run.
