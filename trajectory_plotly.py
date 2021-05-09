import pandas as pd
from datetime import datetime, timedelta
from plotly.offline import plot
import plotly.graph_objects as go
import math
import numpy as np

df = pd.read_csv('districtwise_cases_last_7_days_redone(1day_min_periods).csv')

# taking values where where last 7 days cases are not nan
df = df[df['cases_in_last_7_days'].notna()]

# taking each date and sorting them
dates = df['case_notification_date'].unique()
dates = sorted(dates, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))



# make list of districts
districts = []
for district in df['district']:
    if district not in districts:
        districts.append(district)

# make figure
fig_dict = {'data': [], 'layout': {}, 'frames': []}


# fill in most of layout
fig_dict['layout']['xaxis'] = {'title': 'Total Confirmed Cases','type': 'log', 'range': [0, 5]} #set x axis range 100k
fig_dict['layout']['yaxis'] = {'title': 'New Confirmed Cases (in the Past Week)', 'type': 'log','range': [0, 5]} #set y axis range 100k
fig_dict['layout']['title_text'] = 'Trajectory of Districtwise COVID-19 Confirmed Cases'
fig_dict['layout']['hovermode'] = 'closest'
fig_dict['layout']['margin'] = {
    'l': 100,
    'r': 200,
    'b': 100,
    't': 100,
    'pad': 20,
    }
fig_dict['layout']['updatemenus'] = [{
    'buttons': [{'args': [None, {'frame': {'duration': 500/3,  ###### 1/3 duration of previous one
                'redraw': True}, 'fromcurrent': True,
                'transition': {'duration': 300,
                'easing': 'quadratic-in-out'}}], 'label': 'Play',
                'method': 'animate'}, {'args': [[None],
                {'frame': {'duration': 0, 'redraw': True},
                'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause', 'method': 'animate'}],
    'direction': 'left',
    'pad': {'r': 10, 't': 87},
    'showactive': True,
    'type': 'buttons',
    'x': 0.1,
    'xanchor': 'right',
    'y': 0,
    'yanchor': 'top',
    }]

sliders_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 20},
        'prefix': 'Date:',
        'visible': True,
        'xanchor': 'left',
        },
    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': [],
    }


# make data
date = dates[0]

for district in districts:
    df_by_date = df[df['case_notification_date'] == date]
    df_by_date_and_district = df_by_date[df_by_date['district']
            == district]

    data_dict = {
        'x': list(df_by_date_and_district['cumulative_cases']),
        'y': list(df_by_date_and_district['cases_in_last_7_days']),
        'mode': 'lines+markers',
        'text': list(df_by_date_and_district['district']),
        'name': district,
        }
    fig_dict['data'].append(data_dict)


# creating set of random colors for each district with opacity
# as lines doesn't have any opacity attribute 
districts_line_colors = []
districts_marker_colors = []
for i in range (len(districts)):
    new_color = ('rgba('+str(np.random.randint(0, high = 256))+','+
                str(np.random.randint(0, high = 256))+','+
                str(np.random.randint(0, high = 256)))
    
    temp_dict = {}
    temp_dict['district'] = districts[i]
    temp_dict['color'] = new_color+',0.5)'
    
    districts_line_colors.append(dict(district=districts[i],color=new_color+',0.5)'))   # transparency = 0.5 for lines
    districts_marker_colors.append(dict(district=districts[i],color=new_color+',1)'))   # transparency = 0 for markers


# make frames
# getting all dates and their related values up to consecutive last value to keep previous data points
for index in range(1, len(dates) + 1):

    cumulative_dates = dates[0:index]                               
    frame = {'data': [], 'name': str(cumulative_dates[-1])}         

    for district in districts:
        df_by_date = df[df['case_notification_date'].isin(cumulative_dates)]
        df_by_date_and_district = df_by_date[df_by_date['district']== district]


        # get district line and marker colors
        district_line_color = next(item for item in districts_line_colors if item["district"] == district)['color']
        district_marker_color = next(item for item in districts_marker_colors if item["district"] == district)['color']



        # opacity value = 1 and text value = district name for newest marker 
        opacity_values = [1]
        text_values = [district]
        
        length_df = len(list(df_by_date_and_district['cumulative_cases']))
        
        if length_df != 0:
            opacity_values = []
            text_values = []
            for index in range(length_df):
                if index == length_df-1:
                    opacity_values.append(1)
                    text_values.append(district)
                else:
                    opacity_values.append(0)
                    text_values.append('')
                    
        data_dict = {
            'x': list(df_by_date_and_district['cumulative_cases']),
            'y': list(df_by_date_and_district['cases_in_last_7_days']),
            'mode': 'lines+markers',
            'text': text_values,
            'name': district,
            'customdata' : list(df_by_date_and_district['case_notification_date']),
            'hovertemplate': district+'<br> %{customdata} <br>Total Confirmed Cases: %{x} <br>Weekly Confirmed Cases: %{y}<extra></extra>',
            'marker' : dict(opacity = opacity_values,color = district_marker_color),
            'textposition' : 'bottom right',
            'line': dict( color = district_line_color)
            }
        
        frame['data'].append(data_dict)
        
        

    fig_dict['frames'].append(frame)
    slider_step = {'args': [[cumulative_dates[-1]],
                   {'frame': {'duration': 300, 'redraw': False},
                   'mode': 'immediate',
                   'transition': {'duration': 300}}],
                   'label': cumulative_dates[-1], 'method': 'animate'}
    sliders_dict['steps'].append(slider_step)

fig_dict['layout']['sliders'] = [sliders_dict]
fig = go.Figure(fig_dict)


# doubling times list
doubling_time_in_days =[2,4,8]

for value in doubling_time_in_days:
    doubling_time_in_day = value
    growth_rate = 2 ** (1 / doubling_time_in_day) - 1           # from the formula , doubling period = log(2) / log(1 + growth rate)
    case = 0.01
    dt = [case]

    # make data for n day doubling time of confirmed cases line

    #extending the lines by point
    line_extend = 0
    if value == 2:
        line_extend -= 500
    if value == 4:
        line_extend += 100
    if value == 8:
        line_extend += 500
    while case <= df['cases_in_last_7_days'].max()+line_extend:
        case = case * (1 + growth_rate)
        dt.append(case)

    dt = pd.DataFrame(dt, columns=['per_day_cases'])
    dt['last_7_day_cases'] = dt.rolling(7).sum()
    dt['total_cases'] = dt['per_day_cases'].cumsum()


    # trace for the line
    trace_line = go.Scatter(
    x = list(dt['total_cases']),
    y = list(dt['last_7_day_cases']),
    name = str(value)+' days doubling time of confirmed cases',
    mode = 'lines',
    line = dict(width = 2, color = 'gray', dash = 'dot'),
    textposition = 'top right',
    hoverinfo = 'skip',
    legendgroup=str(value),
    )

    # trace for the text // used scatter instead of annotations for grouping the legend
    trace_text = go.Scatter(
            x= [list(dt['total_cases'])[-1]],
            y= [list(dt['last_7_day_cases'])[-1]+200],
            name = str(value)+' days doubling time of confirmed cases',
            mode = 'text',
            text= str(value)+' days doubling time of confirmed cases',
            hoverinfo = 'skip',
            showlegend = False,
            legendgroup = str(value)
    )

    # default selected line only for 2 // remove to select all by default
    if (value != 2):
        trace_line['visible'] = 'legendonly'
        trace_text['visible'] = 'legendonly'
    
    if (value == 8):
        trace_text['x'] = [list(dt['total_cases'])[-1]+2000]
        trace_text['y'] = [list(dt['last_7_day_cases'])[-1]+2000]
        
    
    
    fig.add_trace(trace_line)
    fig.add_trace(trace_text)
    fig.update_layout(showlegend=True)

# setting legend title text
fig.update_layout(legend_title_text='Districts(Double click to isolate one)')


plot(fig)

