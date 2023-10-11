import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

test_name = "media_deployed_autoscaled"

df = pd.read_csv('test_scripts/data/' + test_name + '.csv')
waiting = df.loc[(df['metric_name'] == 'http_req_waiting') | (df['metric_name'] == 'http_reqs') | (df['metric_name'] == 'checks')].reset_index()
waiting = waiting[['timestamp', 'metric_name', 'metric_value']]

http_reqs_grouped = waiting.loc[waiting['metric_name'] == 'http_reqs'].groupby('timestamp').sum(numeric_only=True).reset_index().rename(columns={'metric_value':'http_reqs'})

http_reqs_failed = waiting.loc[waiting['metric_name'] == 'checks'].groupby('timestamp').sum(numeric_only=True).reset_index().rename(columns={'metric_value':'checks'})

waiting_grouped = waiting.loc[waiting['metric_name'] == 'http_req_waiting'].groupby('timestamp').mean(numeric_only=True).reset_index().rename(columns={'metric_value':'http_req_waiting'})

vus = df.loc[df['metric_name'] == 'vus'].reset_index()
vus = vus[['timestamp', 'metric_value']].rename(columns={'metric_value':'vus'})

http_reqs_grouped['timestamp'] = pd.to_datetime(http_reqs_grouped['timestamp'], unit='s')
waiting_grouped['timestamp'] = pd.to_datetime(waiting_grouped['timestamp'], unit='s')
vus['timestamp'] = pd.to_datetime(vus['timestamp'], unit='s')
http_reqs_failed['timestamp'] = pd.to_datetime(http_reqs_failed['timestamp'], unit='s')

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
x=http_reqs_grouped['timestamp'], y=http_reqs_grouped['http_reqs'], name='Requests per Second'))

fig.add_trace(go.Scatter(
x=waiting_grouped['timestamp'], y=waiting_grouped['http_req_waiting'], name='Response Time in Milliseconds'), secondary_y=True)

fig.add_trace(go.Scatter(
x=vus['timestamp'], y=vus['vus'], name='Number of Workers'), secondary_y=True)

fig.add_trace(go.Scatter(
x=vus['timestamp'], y=http_reqs_failed['checks'], name='Failed Requests'))

fig.update_yaxes(title_text="Response Time (ms), # of Workers", secondary_y=True)

fig.update_layout(title_text="Media Service")

fig.write_html("test_scripts/data/" + test_name + ".html")