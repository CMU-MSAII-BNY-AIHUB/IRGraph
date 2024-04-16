from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d
from bokeh.io import show
import numpy as np
import pandas as pd

dates = np.array(pd.date_range('2023-01-01', periods=10), dtype=np.datetime64)
share_prices = np.linspace(100, 200, 10)  
volumes = np.linspace(1000, 5000, 10)  

p = figure(x_axis_type="datetime", width=700, height=300, y_range=(min(share_prices) * 0.9, max(share_prices) * 1.1))

p.line(dates, share_prices, color='blue', legend_label='Share Price')

p.extra_y_ranges = {"volume": Range1d(start=min(volumes) * 0.9, end=max(volumes) * 1.1)}
p.add_layout(LinearAxis(y_range_name="volume", axis_label="Volume"), 'right')

p.vbar(x=dates, top=volumes, width=0.9, y_range_name="volume", color='green', alpha=0.5, legend_label='Volume')

p.legend.location = "top_left"

show(p)