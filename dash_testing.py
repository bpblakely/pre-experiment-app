import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.express as px
import pandas as pd
from datetime import date

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


df = pd.read_csv(r'G:\Python File Saves\final_out_new_method.csv',parse_dates=['date'])
df['date'] = df['date'].apply(lambda x: x.date())

min_date = df['date'].min()
max_date = df['date'].max()

summarized = df.groupby(['estMethod','velComp']).mean()
summarized.reset_index(inplace=True)  

columns = ['totalTweets', 'estimatedTweets', 'span','knots', 'absRelBias', 'mab', 'rmsd', 'tstat', 'pval']
regions = list(df.region.unique())

x_value = "estMethod"
y_value = "totalTweets"
color_value = "velComp"

fig = px.bar(summarized, x= x_value, y= y_value, color=color_value, barmode="group")
test_fig = px.box(df, x= x_value, y= y_value, color=color_value, points="outliers")

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
        html.Div('Select Date Range', style={'color': 'black', 'fontSize': 14,'font-weight':'bold'}),
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            initial_visible_month=min_date,
            start_date = min_date,
            end_date=max_date
        ),
        html.Div(id='output-container-date-picker-range', style = {'color':'grey','fontSize':12}),
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


def create_figure(x,y,color,title,df):
    fig = px.bar(df, x=x, y= y, color=color, barmode="group",title = title)
    return fig

def create_boxplot(x,y,color,title,df):
    fig = px.box(df, x=x, y= y, color=color, points="outliers",title = title)
    return fig

@app.callback([dash.dependencies.Output('example-graph', 'figure'),
            dash.dependencies.Output('test-graph', 'figure'),   
            dash.dependencies.Output('output-container-date-picker-range', 'children'),
            ], 
              [dash.dependencies.Input('input', 'value'),
              dash.dependencies.Input('my-boolean-switch', 'on'),
              dash.dependencies.Input('my-date-picker-range', 'start_date'),
              dash.dependencies.Input('my-date-picker-range', 'end_date'),
              dash.dependencies.Input('region_dropdown', 'value'),
              dash.dependencies.State('example-graph', 'figure'),
              dash.dependencies.State('test-graph', 'figure'),
              ])
def update_figure(selected_value,on,start_date, end_date,seleceted_regions,bar_current, box_current):
    global x_value, y_value,color_value
    
    # Select date span
    start_date_object = date.fromisoformat(start_date)
    end_date_object = date.fromisoformat(end_date)
    
    days_spanned = (end_date_object - start_date_object).days
    days_spanned_string = f"Number of days spanned: {days_spanned}"
    region_names = ', '.join([region.split('-')[0] for region in regions])
    if on:
        title = f"{selected_value} by estMethod for {region_names} over {days_spanned} days"
    else:
        title = f"{selected_value} by velComp for {region_names} over {days_spanned} days"

    # Handle bad inputs by returning the same graph (unchanged)
    if start_date_object > end_date_object or selected_value == None or len(seleceted_regions) == 0:
        return bar_current,box_current, days_spanned_string

    data = df.loc[(df['date'] >= start_date_object) & (df['date'] <= end_date_object)]
    
    # Select Regions
    data = data.loc[data['region'].isin(seleceted_regions)]

    summarized = data.groupby(['estMethod','velComp']).mean()
    summarized.reset_index(inplace=True)  
    
    if on:
        x_value, color_value = "velComp", "estMethod"
    else:
        x_value, color_value = "estMethod", "velComp"
    
    y_value = selected_value
    if y_value == 'knots':
        summarized = summarized.loc[summarized.estMethod.str.contains('aspline')]
        data = data.loc[data.estMethod.str.contains('aspline')]
        
    elif y_value == 'span':
        summarized = summarized.loc[summarized.estMethod.str.contains('loess')]
        data = data.loc[data.estMethod.str.contains('loess')]

    bar_fig = create_figure(x=x_value,y=y_value,color=color_value,title=title,df = summarized)
    box_fig = create_boxplot(x=x_value,y=y_value,color=color_value,title=title,df = data)
    return bar_fig,box_fig, days_spanned_string

if __name__ == '__main__':
    app.run_server(debug=True)
