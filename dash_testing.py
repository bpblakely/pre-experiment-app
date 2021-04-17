import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.express as px
import pandas as pd
from datetime import date

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title="Pre-experiment Data"

df_old = pd.read_csv(r'final_out.csv',parse_dates=['date'])
df_new = pd.read_csv(r'final_out_new_method.csv',parse_dates=['date'])
df_old['date'] = df_old['date'].apply(lambda x: x.date())
df_new['date'] = df_new['date'].apply(lambda x: x.date())

df = df_old

min_date = df['date'].min()
max_date = df['date'].max()

summarized = df.groupby(['estMethod','velComp']).mean()
summarized.reset_index(inplace=True)

summarized.sort_values(by=['estMethod','velComp'],inplace=True)
df.sort_values(by=['estMethod','velComp'],inplace=True)

columns = ['totalTweets', 'estimatedTweets', 'span','knots', 'absRelBias', 'mab', 'rmsd', 'tstat', 'pval']
regions = list(df.region.unique())

x_value = "estMethod"
y_value = "totalTweets"
color_value = "velComp"

colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

est_color_map = {}
for i,c in enumerate(df["estMethod"].unique()):
    est_color_map[c] = colors[i]
    
vel_color_map = {}
for i,c in enumerate(df["velComp"].unique()):
    vel_color_map[c] = colors[i]

fig = px.bar(summarized, x= x_value, y= y_value, color=color_value, barmode="group",color_discrete_map=vel_color_map)
test_fig = px.box(df, x= x_value, y= y_value, color=color_value, points="outliers",color_discrete_map=vel_color_map)

app.layout = html.Div(children=[
    html.H1(children='Pre-experiment Data Visualization'),

    html.Div(children='''
             Currently, the bar plot is the mean of the selected date range for the selected cities. The box plot is using all the data under the same selected parameters.
             '''
        ),
    html.Br(),
    html.Div(children = [
        html.P("Parameters",style={'fontSize': 18,'font-weight':'bold','text-align':'center'}),
        html.Br(),
        html.Div(children=[
            html.Div(children = [
                html.Div('Select Y-axis', style={'color': 'black', 'fontSize': 14,'font-weight':'bold'}),
                dcc.Dropdown(
                    id = "input",
                    options=[{'label': i, 'value': i} for i in columns],
                    value='totalTweets'
                ),
                ],
            style={"width": "20%"}),
            html.Div(children = [
                html.Div('Select Region', style={'color': 'black', 'fontSize': 14,'font-weight':'bold'}),
                dcc.Dropdown(
                    id = "region_dropdown",
                    options=[{'label': i, 'value': i} for i in regions],
                    value=regions,
                    multi=True
                ),
                ],
                style={"width": "30%","margin":"auto"}),
            ],
            style={"display":'flex'},
        ),
        
        html.Br(),
        html.Div(children=[
            html.Div('Select Date Range', style={'color': 'black', 'fontSize': 14,'font-weight':'bold'}),
            html.Div(children=[
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=min_date,
                    start_date = min_date,
                    end_date=max_date
                ),
                html.Div(
                    daq.BooleanSwitch(
                        id='dataset-switch',
                        on=False,
                        label="New Velocity Method",
                        labelPosition="bottom"
                    ),
                    style={"margin":"auto"}
                )
                ],
                style={"display":'flex'}
            ),
            html.Div(children=[
                html.Div(id='output-container-date-picker-range', style = {'color':'grey','fontSize':12}),
                html.Div(id='output-dataset-switch', style = {'color':'grey','fontSize':12,"margin":"auto"}),
            ], style={"display":'flex'}
            ),
        ]
        ),
    ],
    style= {'background-color': '#f8f9fa','padding': '20px 10px'}
    ),
    html.Br(),
    html.Div(children=[
        html.Br(),
        #html.Div(id='graph-title', style = {'color':'#2B333D','fontSize':18,'text-align':'center','font-weight':'bold'}),
        html.P("Graphs",style={'fontSize': 18,'font-weight':'bold','text-align':'center'}),
        dcc.Graph(
            id='example-graph',
            figure=fig
        ),
        dcc.Graph(
            id='test-graph',
            figure=test_fig
        ),

        html.Div(children = [
            daq.BooleanSwitch(
                id='my-boolean-switch',
                on=False,
                label="Group by velComp",
                labelPosition="bottom"
            ),
            ]
        ),
    ],
    )
],style = {"background-color":'milk'})


def create_figure(x,y,color,title,color_map,df):
    fig = px.bar(df, x=x, y= y, color=color, barmode="group",title = title,color_discrete_map=color_map)
    return fig

def create_boxplot(x,y,color,title,color_map,df):
    fig = px.box(df, x=x, y= y, color=color, points="outliers",title = title,color_discrete_map=color_map)
    return fig

@app.callback([dash.dependencies.Output('example-graph', 'figure'),
            dash.dependencies.Output('test-graph', 'figure'),   
            dash.dependencies.Output('output-container-date-picker-range', 'children'),
            dash.dependencies.Output('output-dataset-switch', 'children'),
            ], 
              [dash.dependencies.Input('input', 'value'),
              dash.dependencies.Input('my-boolean-switch', 'on'),
              dash.dependencies.Input('dataset-switch', 'on'),
              dash.dependencies.Input('my-date-picker-range', 'start_date'),
              dash.dependencies.Input('my-date-picker-range', 'end_date'),
              dash.dependencies.Input('region_dropdown', 'value'),
              dash.dependencies.State('example-graph', 'figure'),
              dash.dependencies.State('test-graph', 'figure'),
              ])
def update_figure(selected_value,on,data_switch,start_date, end_date,seleceted_regions,bar_current, box_current):
    global x_value, y_value,color_value,df
    
    # Select date span
    start_date_object = date.fromisoformat(start_date)
    end_date_object = date.fromisoformat(end_date)
    
    days_spanned = (end_date_object - start_date_object).days
    days_spanned_string = f"Number of days spanned: {days_spanned}"
    region_names = ', '.join([region.split('-')[0] for region in seleceted_regions])
    if on:
        title = f"{selected_value} by velComp for {region_names} over {days_spanned} days"
    else:
        title = f"{selected_value} by estMethod for {region_names} over {days_spanned} days"

    dataset_string = "Using "
    if data_switch:
        df = df_new
        dataset_string += "new velocity method"
    else:
        df = df_old
        dataset_string += "old velocity method"
    # Handle bad inputs by returning the same graph (unchanged)
    if start_date_object > end_date_object or selected_value == None or len(seleceted_regions) == 0:
        return bar_current,box_current, days_spanned_string,dataset_string

    data = df.loc[(df['date'] >= start_date_object) & (df['date'] <= end_date_object)]
    
    # Select Regions
    data = data.loc[data['region'].isin(seleceted_regions)]

    summarized = data.groupby(['estMethod','velComp']).mean()
    summarized.reset_index(inplace=True)  

    summarized.sort_values(by=['estMethod','velComp'],inplace=True,ascending= True)
    data.sort_values(by=['estMethod','velComp'],inplace=True)

    if on:
        x_value, color_value = "velComp", "estMethod"
        color_map = est_color_map
    else:
        x_value, color_value = "estMethod", "velComp"
        color_map = vel_color_map
    
    y_value = selected_value
    if y_value == 'knots':
        summarized = summarized.loc[summarized.estMethod.str.contains('aspline')]
        data = data.loc[data.estMethod.str.contains('aspline')]
        
    elif y_value == 'span':
        summarized = summarized.loc[summarized.estMethod.str.contains('loess')]
        data = data.loc[data.estMethod.str.contains('loess')]

    bar_fig = create_figure(x=x_value,y=y_value,color=color_value,title=title,color_map=color_map,df = summarized)
    box_fig = create_boxplot(x=x_value,y=y_value,color=color_value,title=title,color_map=color_map,df = data)
    return bar_fig,box_fig, days_spanned_string,dataset_string

if __name__ == '__main__':
    app.run_server()
