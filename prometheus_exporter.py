from typing import Dict, Iterator

import time
import os
import prefect
import dateutil.parser

from flask import Flask, Response

from prometheus_client import generate_latest, REGISTRY, start_http_server
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.samples import Sample


PREFECT_API_KEY=os.environ['PREFECT_API_KEY']

client = prefect.Client(api_key=PREFECT_API_KEY)


def _add_gauge_metric(metric, labels, value):
    metric.samples.append(Sample(
        metric.name, labels,
        value, 
        None
    ))


def fetch_all(client: prefect.Client, query: str) -> Iterator[Dict]:
    offset = 0

    while True:
        res = client.graphql(query, variables={'offset': offset})
        yield res

        count = res['data']['res']['aggregate']['count']
        if count < 100:
            break
    
        offset += 100


def to_metrics(res: Dict):
    for i in res['data']['res']['nodes']:
        yield (
            {
                'state': i['state'],
                'project': i['flow']['project']['name'],
                'flow': i['flow']['name'],
                **{f'param__{k}': str(v) for (k,v) in i['parameters'].items()}
            },
            dateutil.parser.parse(i['state_timestamp']).timestamp()
        )


class PrefectCollector:
    def describe(self):
        return []
    
    def collect(self):
        flow_run_last_state = GaugeMetricFamily(
            'prefect_flow_run_last_state_ts',
            'Metric that captures timestamp of last Successful and Failed runs of each flow with each unique parameters set',
            labels=['state', 'project', 'flow']
        )

        for res in fetch_all(client, """
query($offset: Int) {
  res: flow_run_aggregate(
    distinct_on: [flow_id, state, parameters]
    where: {
      state: {_in: ["Success", "Failed"]}
      flow: {
        archived: {_eq: false}
      }
    }
    offset: $offset
    order_by: [
      {flow_id: asc}
      {state: asc}
      {parameters: asc}
      {state_timestamp: desc_nulls_last}
    ]
  ) {
    aggregate {
      max {
        state_timestamp
      }
      count
    }
    nodes {
      flow {
        name
        project {
          name
        }
      }
      parameters
      state
      state_timestamp
    }
  }
}
        """):
            for labels, value in to_metrics(res):
                _add_gauge_metric(flow_run_last_state, labels, value)
        
        yield flow_run_last_state
                

REGISTRY.register(PrefectCollector())


app = Flask(__name__)


@app.route('/')
def ok():
    return 'ok'


@app.route('/metrics/')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
