from logging import log
from bokeh.layouts import column, gridplot, row
from bokeh.models.annotations import ColorBar, Legend, LegendItem, Title
from bokeh.models.glyphs import Circle
from bokeh.models import CustomJS, Dropdown,ColumnDataSource, CheckboxGroup,HoverTool
from bokeh.models.transforms import LinearInterpolator
from bokeh.models import CheckboxButtonGroup,DateRangeSlider
from bokeh.palettes import Blues256, Colorblind, Magma256, Oranges, Category20,\
    Turbo256, Viridis256, mpl,Spectral6,viridis,turbo,Spectral,Plasma,inferno,Set3,all_palettes
from bokeh.transform import linear_cmap
from bokeh.models.widgets import Select,MultiSelect, Slider
from numpy import sqrt, square
import numpy as np
from numpy.core.arrayprint import format_float_positional
import pandas as pd
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.transform import cumsum
from math import pi
from bokeh.palettes import Category20c
from bokeh.models import RadioButtonGroup,Legend,SingleIntervalTicker
import os
from datetime import date

def get_data():
    stockprice = {}
    companys=[]
    file_path = "sharePrice"
    for filename in os.listdir(file_path):

        if os.path.isfile(os.path.join(file_path, filename)):
            print(filename)
            company_name = filename.split('-')[0].strip()
            companys.append(company_name)
            data = pd.read_excel(os.path.join(file_path, filename), skiprows=35)
            
            data.rename(columns={col: 'Volume' for col in data.columns if 'Volume' in col}, inplace=True)
            data.rename(columns={col: 'Share Pricing' for col in data.columns if 'Share Pricing' in col}, inplace=True)
            stockprice[company_name] = data
    return stockprice,companys

def datetime(x):
    print(np.array(x, dtype=np.datetime64))
    return np.array(x, dtype=np.datetime64)

bokeh_doc=curdoc()
stockprice,companys = get_data()

all_dates = np.concatenate([stockprice[company]['Dates'].values for company in companys])
min_date, max_date = np.min(all_dates), np.max(all_dates)


stockprice,companys = get_data()

def callback1(new):
    switch=checkbox_button_group.active
    for x in range(0,len(lines)):
        if x in switch:
            lines[x].visible=True
        else:
            lines[x].visible=False

checkbox_button_group = CheckboxGroup(labels=companys, active=list(range(0,len(companys))))
checkbox_button_group.on_click(callback1)



def callback2(attr, old, new):
    selected_range = date_range_slider.value_as_datetime
    start_date, end_date = selected_range
    for line, company in zip(lines, companys):
        new_data = stockprice[company][(stockprice[company]['Dates'] >= start_date) & (stockprice[company]['Dates'] <= end_date)]
        line.data_source.data = {'x': datetime(new_data['Dates']), 'y': new_data['Share Pricing']}



date_range_slider = DateRangeSlider(title="Select Date Range:", start=min_date, end=max_date, value=(min_date, max_date), step=1)
date_range_slider.on_change('value', callback2)

def main_plot():
    p1 = figure(x_axis_type="datetime", title="Sharing Prices", width=1600, height=800)
    p1.grid.grid_line_alpha = 0.3
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Share Price'
    colors = ['#A6CEE3', '#B2DF8A', '#33A02C', '#FB9A99']
    lines = []
    
    hover_tool = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Share Price", "@y"),
    ], formatters={'@x': 'datetime'}, mode='vline')

    p1.add_tools(hover_tool)

    for i, company in enumerate(companys):
        source = ColumnDataSource(data={
            'x': datetime(stockprice[company]['Dates']),
            'y': stockprice[company]['Share Pricing']
        })
        line = p1.line('x', 'y', source=source, color=colors[i], legend_label=company)
        lines.append(line)
        # Add circles for hover effect, invisible (size=0)
        p1.circle('x', 'y', source=source, size=0, hover_fill_color='red', hover_alpha=0.5)

    p1.legend.location = "top_left"
    layout = row(column(checkbox_button_group, date_range_slider), p1)
    return p1, layout, lines


plot,layout,lines = main_plot()
bokeh_doc.title = "stock price"
bokeh_doc.add_root(layout)