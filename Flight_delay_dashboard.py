import pandas as pd
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash import no_update

# Read the airline data into pandas dataframe
airline_data = pd.read_csv('airline_data.csv')

# Create a dash application
app = dash.Dash(__name__)
# app.config.suppress_callback_exceptions = True

"""Compute graph data for creating yearly airline performance report 

Function that takes airline data as input and create 5 dataframes based on the grouping condition to be used for plottling charts and grphs.

Argument:
     
    df: Filtered dataframe
    
Returns:
   Dataframes to create graph. 
"""

def computed_data_choice1(df):
    print(df.head())
    # cancellation Category count
    df_bar = df.groupby(['Month', 'CancellationCode'])['Flights'].sum().reset_index()
    # Avg flight time by reporting Airline
    df_line = df.groupby(['Month', 'Reporting_Airline'])['AirTime'].mean().reset_index()
    # % diverted airport landings per reporting airline
    df_pie = df[df['DivAirportLandings']!=0]
    # state and flights
    df_map = df.groupby(['OriginState'])['Flights'].sum().reset_index()

    df_tree = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()

    return df_bar, df_line, df_pie, df_map, df_tree

"""Compute graph data for creating yearly airline delay report

This function takes in airline data and selected year as an input and performs computation for creating charts and plots.

Arguments:
    df: Input airline data.
    
Returns:
    Computed average dataframes for carrier delay, weather delay, NAS delay, security delay, and late aircraft delay.
"""

def computed_data_choice2(df):
    # Compute delay averages
    car_del = df.groupby(['Month', 'Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    weather_del = df.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    NAS_del = df.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
    sec_del = df.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    late_del = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()

    return car_del, weather_del, NAS_del, sec_del, late_del

app.layout = html.Div(children=[html.H1('US Domestic Airline Flights Performance',
                                style={'textAlign': 'center', 'color':'#503D36', 'font-size': 30}),
                                html.Div([html.H2('Report Type: ', style={'margin-right': '5px'}), 
                                # Dropdown creation
                                # Create an outer division 
                                # Create an division for adding dropdown helper text for report typ
                                dcc.Dropdown(id='performance-report',
                                options=[{'label':'Yearly Airline Performance Report', 'value': 'perf'},
                                        {'label': 'Yearly Airline Delay Report', 'value': 'del'}],
                                        placeholder='Select a report type',
                                        style={'width': '80%', 'padding':'6px', 'font-size':'20px',
                                                'textAlign': 'left', 'top': '9px', 'line-height':2.3})],
                                style={'display': 'flex'}),
                                e
                                # Create an division for adding dropdown helper text for choosing year
                                html.Div([html.H2('Chose Year: ', style={'margin-right': '5px'}), 
                                dcc.Dropdown(id='delay-report',
                                # Update dropdown values using list comphrehension
                                options=[{'label':i, 'value':i} for i in [i for i in range(2005, 2021, 1)]],
                                        placeholder='Select a Year',
                                        style={'width': '80%', 'padding':'6px', 'font-size':'20px',
                                                'textAlign': 'left', 'top': '9px', 'line-height':2.3})],
                                style={'display': 'flex'}),
                                html.Div(dcc.Graph(id='plot1')),
                                html.Div([html.Div(dcc.Graph(id='plot2')), html.Div(dcc.Graph(id='plot3'))],
                                    style={'display': 'flex'}),
                                html.Div([html.Div(dcc.Graph(id='plot4')), html.Div(dcc.Graph(id='plot5'))],
                                    style={'display': 'flex'})
                                
                                ])
#  Callback function definition
@app.callback([Output(component_id='plot1', component_property='figure'),
                Output(component_id='plot2', component_property='figure'),
                Output(component_id='plot3', component_property='figure'),
                Output(component_id='plot4', component_property='figure'),
                Output(component_id='plot5', component_property='figure')], 
                [Input(component_id='performance-report', component_property='value'),
                Input(component_id='delay-report', component_property='value')],
                # Holding output state till user enters all the form information. In this case, it will be chart type and year
                [State("plot1", 'figure'), State("plot2", "figure"),
                State("plot3", "figure"), State("plot4", "figure"),
                State("plot5", "figure")
               ])
# Add computation to callback function and return graph
def get_graph(chart, year, children1, children2, children3, children4, children5):
    print(type(year))
    df = airline_data[airline_data['Year'] == year]
    if chart == 'perf':
        df_bar, df_line, df_pie, df_map, df_tree = computed_data_choice1(df)
        bar_fig = px.bar(df_bar, x='Month', y='Flights', color='CancellationCode', title='Monthly Flight Cancellation')
        line_fig = px.line(df_line, x='Month', y='AirTime', color='Reporting_Airline', title='Monthly Avg Flight Time')
        pie_fig = px.pie(df_pie, values='Flights', names='Reporting_Airline', title='% of flights by reporting airline')
        map_fig = px.choropleth(df_map, locations='OriginState', color='Flights',
                                hover_data=['OriginState', 'Flights'], locationmode='USA-states',
                                color_continuous_scale='GnBu',
                                range_color=[0, df_map['Flights'].max()])
        map_fig.update_layout(
                    title_text = 'Number of flights from origin state', 
                    geo_scope='usa') # Plot only the USA instead of globe
                    
        # Number of flights flying to each state from each reporting airline
        tree_fig = px.treemap(df_tree, path=['DestState', 'Reporting_Airline'],
                                values='Flights',
                                color='Flights',
                                color_continuous_scale='RdBu',
                                title='Flight count by airline to destination state')

        # Return dcc.Graph component to the empty division
        return [bar_fig, 
                line_fig,
                pie_fig,
                map_fig,
                tree_fig
                ]
    else:
        # Compute required information for creating graph from the data
        car_del, weather_del, NAS_del, sec_del, late_del = computed_data_choice2(df)
        
        # Create graph
        carrier_fig = px.line(car_del, x='Month', y='CarrierDelay', color='Reporting_Airline', title='Average carrrier delay time (minutes) by airline')
        weather_fig = px.line(weather_del, x='Month', y='WeatherDelay', color='Reporting_Airline', title='Average weather delay time (minutes) by airline')
        nas_fig = px.line(NAS_del, x='Month', y='NASDelay', color='Reporting_Airline', title='Average NAS delay time (minutes) by airline')
        sec_fig = px.line(sec_del, x='Month', y='SecurityDelay', color='Reporting_Airline', title='Average security delay time (minutes) by airline')
        late_fig = px.line(late_del, x='Month', y='LateAircraftDelay', color='Reporting_Airline', title='Average late aircraft delay time (minutes) by airline')
        
        return[carrier_fig, 
                weather_fig, 
                nas_fig, 
                sec_fig, 
                late_fig]

if __name__ == '__main__':
    app.run_server()