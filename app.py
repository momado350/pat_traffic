import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

circulation = pd.read_csv('data/M.Ahmed Charge Hist log output with IDs.csv', parse_dates=['Trans Hist Date'])
# import pyodbc
# conn = pyodbc.connect('Driver={SQL Server};'
#                       'Server=kcplsql;'
#                       'Database=KCPL_TBS_Archive;'
#                       'Trusted_Connection=yes;')

# computer = pd.read_sql_query('SELECT * FROM MyPC3SessionAudit WHERE StartTime > ?', conn, parse_dates=['StartTime'], params=['2022-01-21 20:26:15'])
computer = pd.read_csv('data/computer.csv', parse_dates=['StartTime'])

# computer data
mask = computer['SiteName'].isin(['__Not In Use', '_default', '_IS Testing Lab'])
computer = computer[~mask]
replace_values = {'Lucile H. Bluford Branch': 'KC-BLUFORD', 'Plaza Branch': 'KC-PLAZA', 'Central Library': 'KC-CENTRAL', 'Waldo Branch': 'KC-WALDO', 'Southeast Branch': 'KC-SE', 'North-East Branch': 'KC-NE', 'Trails West Branch': 'KC-TRAILS', 'Westport Branch': 'KC-WSTPORT', 'Irene H. Ruiz Biblioteca de las Americas': 'KC-RUIZ', 'Sugar Creek Branch': 'KC-SGCREEK'}
computer = computer.replace({"SiteName": replace_values})
computer1 = computer[['StartTime', 'EndTime', 'SessionID', 'SiteName']]
computer1['Date'] = computer1['StartTime'].dt.date
computer1['time'] = computer1['StartTime'].dt.time
computer1['year'] = computer1['StartTime'].dt.year
computer1['week_day'] = computer1['StartTime'].dt.day_name()
computer1['time'] = computer1['time'].astype(str)
computer1['hour'] = computer1['time'].str.split(':').str[0]
computer1['hour'] = computer1['hour'].astype(int)
computer1['date'] = pd.to_datetime(computer1['Date'])
grouped = computer1.groupby(['date','SiteName', 'hour'])['SessionID'].count().reset_index()
replace_values = {8: '8 AM', 9: "9 AM", 10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM", 15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM", 20: "8 PM", 21: '9'}
computer_df = grouped.replace({"hour": replace_values})
computer_df.rename(columns={'date': 'Trans Hist Date', 'SiteName': 'Station Library Checkout', 'hour': 'hours'}, inplace=True)
mask1 = circulation['User Profile'].isin(['MISSING', 'KC-DISPLAY', 'KC-MAINT', 'DISCARD', 'KC-STAFF', 'DAMAGED', 'KC-CATALOG', 'KC-SUSPND',
 'LOST', 'KCP-ILL', 'KC-COLDEV', 'KC-TFRBTG', 'KC_CAT1', 'REPLACE'])
circulation = circulation[~mask1]
circulation['trans_time'] = circulation['Trans Hist Datetime'].str.split(' ').str[1]
circulation['hour'] = circulation['trans_time'].str.split(':').str[0]
circulation1 = circulation.groupby(['Trans Hist Date', 'Station Library Checkout', 'hour'])['User Id'].unique().reset_index()
## circulation1 = pd.DataFrame(circulation1)
#circulation1['patron'] = circulation['User Id'].unique()
circulation1['patrons'] = circulation1['User Id'].apply(lambda x: len(x))#.reset_index()
circulation2 = circulation1[['Trans Hist Date', 'Station Library Checkout', 'hour', 'patrons']]
#circulation2['patrons'] = circulation2['patrons'].fillna(0)
circulation2['hours'] = circulation2['hour'].astype(int)
circulation2['week_day'] = circulation2['Trans Hist Date'].dt.day_name()
replace_values = {9: "9 AM", 10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM", 15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM", 20: "8 PM"}
circulation2 = circulation2.replace({"hours": replace_values})
mer_df = pd.merge(circulation2, computer_df)
mer_df['total'] = mer_df['SessionID'] + mer_df['patrons']

covid_data_1 = mer_df.groupby(['Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
covid_data_1w = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
covid_data_1m = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='M')])[['patrons', 'SessionID', 'total']].sum().reset_index()

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('lib_logo.png'),
                     id = 'corona-image',
                     style={'height': '60px',
                            'width': 'auto',
                            'margin-bottom': '25px'})


        ], className='one-third column'),

        html.Div([
            html.Div([
                html.H3('Patrons Traffic Dashboard', style={'margin-bottom': '0px', 'color': 'white'}),
                html.H5('Track Patron Traffic by Library Branch', style={'margin-bottom': '0px', 'color': 'white'})
            ])

        ], className='one-half column', id = 'title'),

        html.Div([
            html.H6('Last Updated: ' + str(mer_df['Trans Hist Date'].iloc[-1].strftime('%B %d, %Y')) + ' 00:01 (UTC)',
                    style={'color': 'orange'})

        ], className='one-third column', id = 'title1')

    ], id = 'header', className= 'row flex-display', style={'margin-bottom': '25px'}),

    html.Div([
        html.Div([
            html.H6(children='All Year to Date Traffic',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1['total'].sum():,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Last Month: ' + f"{covid_data_1m['total'].iloc[-1]:,.0f}"
                   + ' (' + str(round(((covid_data_1m['total'].iloc[-1]) /
                                   covid_data_1['total'].sum()) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children='All Last Week,s Total',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['total'].iloc[-1]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['total'].iloc[-2]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['total'].iloc[-1]) /
                                   covid_data_1w['total'].iloc[-2]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children="All Last Week's Computer Usage",
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['SessionID'].iloc[-1]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['SessionID'].iloc[-2]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['SessionID'].iloc[-1]) /
                                   covid_data_1w['SessionID'].iloc[-2]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children="All Last Week's Circulation",
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['patrons'].iloc[-1]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['patrons'].iloc[-2]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['patrons'].iloc[-1]) /
                                   covid_data_1w['patrons'].iloc[-2]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

    ], className='row flex display'),

    html.Div([
        html.Div([
            html.P('Select Branch:', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(id = 'w_countries',
                         multi = False,
                         searchable= True,
                         value='KC-PLAZA',
                         placeholder= 'Select Countries',
                         options= [{'label': c, 'value': c}
                                   for c in (mer_df['Station Library Checkout'].unique())], className='dcc_compon'),
            html.P('Branch Traffic: ' + ' ' + str(mer_df['Trans Hist Date'].iloc[-1].strftime('%B %d, %Y')),
                   className='fix_label', style={'text-align': 'center', 'color': 'white'}),
            dcc.Graph(id = 'confirmed', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'death', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'recovered', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
# dcc.Graph(id = 'active', config={'displayModeBar': False}, className='dcc_compon',
#                       style={'margin-top': '20px'})

        ], className='create_container three columns'),

        html.Div([
dcc.Graph(id = 'pie_chart', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container four columns'),

html.Div([
dcc.Graph(id = 'line_chart', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container five columns'),

    ], className='row flex-display'),

#     html.Div([
# html.Div([
# dcc.Graph(id = 'map_chart', config={'displayModeBar': 'hover'}
#                       )
#         ], className='create_container1 twelve columns')

#     ], className='row flex-display')

], id = 'mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

@app.callback(Output('confirmed', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    mer_df_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_confirmed = mer_df_2[mer_df_2['Station Library Checkout'] == w_countries]['total'].iloc[-1]
    delta_confirmed = mer_df_2[mer_df_2['Station Library Checkout'] == w_countries]['total'].iloc[-2] 

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_confirmed,
               delta = {'reference': delta_confirmed,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Week Total',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('death', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_death = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].iloc[-1]
    delta_death = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].iloc[-2]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_death,
               delta = {'reference': delta_death,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Week Computer Usage',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('recovered', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_recovered = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].iloc[-1]
    delta_recovered = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].iloc[-2]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_recovered,
               delta = {'reference': delta_recovered,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Week Circulation',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

# @app.callback(Output('active', 'figure'),
#               [Input('w_countries','value')])
# def update_confirmed(w_countries):
#     covid_data_2 = covid_data.groupby(['date', 'Station Library Checkout'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
#     value_active = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-1] - covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-2]
#     delta_active = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-2] - covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-3]

#     return {
#         'data': [go.Indicator(
#                mode='number+delta',
#                value=value_active,
#                delta = {'reference': delta_active,
#                         'position': 'right',
#                         'valueformat': ',g',
#                         'relative': False,
#                         'font': {'size': 15}},
#                number={'valueformat': ',',
#                        'font': {'size': 20}},
#                domain={'y': [0, 1], 'x': [0, 1]}
#         )],

#         'layout': go.Layout(
#             title={'text': 'New Active',
#                    'y': 1,
#                    'x': 0.5,
#                    'xanchor': 'center',
#                    'yanchor': 'top'},
#             font=dict(color='#e55467'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height = 50,

#         )
#     }

@app.callback(Output('pie_chart', 'figure'),
              [Input('w_countries','value')])
def update_graph(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', 'Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
    confirmed_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].sum()
    death_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].sum()
    recovered_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['total'].sum()
    #active_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-1]
    colors = ['orange', 'blue']

    return {
        'data': [go.Pie(
            # labels=['Circulation', 'Computer', 'Total of Both'],
            labels=['Circulation', 'Computer'],
            values=[confirmed_value, death_value, recovered_value],
            marker=dict(colors=colors),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': 'Branch Total (Year to Date): ' + (w_countries),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7}


        )
    }

@app.callback(Output('line_chart', 'figure'),
              [Input('w_countries','value')])
def update_graph(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout','Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
    covid_data_3 = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries][['Station Library Checkout', 'Trans Hist Date', 'total']].reset_index()
    covid_data_3['daily confirmed'] = covid_data_3['total'].shift(1)
    covid_data_3['Rolling Ave.'] = covid_data_3['total'].rolling(window=7).mean()


    return {
        'data': [go.Bar(
            x=covid_data_3['Trans Hist Date'].tail(30),
            y=covid_data_3['daily confirmed'].tail(30),
            name='Daily Patron Traffic',
            marker=dict(color='orange'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + covid_data_3['Trans Hist Date'].tail(30).astype(str) + '<br>' +
            '<b>Daily Traffic Numbers</b>: ' + [f'{x:,.0f}' for x in covid_data_3['daily confirmed'].tail(30)] + '<br>' +
            '<b>Branch</b>: ' + covid_data_3['Station Library Checkout'].tail(30).astype(str) + '<br>'


        ),
            go.Scatter(
                x=covid_data_3['Trans Hist Date'].tail(30),
                y=covid_data_3['Rolling Ave.'].tail(30),
                mode='lines',
                name='Rolling Average of the last 7 days - daily Patron Traffic',
                line=dict(width=3, color='#FF00FF'),
                hoverinfo='text',
                hovertext=
                '<b>Date</b>: ' + covid_data_3['Trans Hist Date'].tail(30).astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_3['Rolling Ave.'].tail(30)] + '<br>'


            )],

        'layout': go.Layout(
            title={'text': 'Last 30 Days Daily Patron Traffic: ' + (w_countries),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Patron Traffic</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )


        )
    }

# @app.callback(Output('map_chart', 'figure'),
#               [Input('w_countries','value')])
# def update_graph(w_countries):
#     covid_data_4 = covid_data.groupby(['Lat', 'Long', 'Station Library Checkout'])[['confirmed', 'death', 'recovered', 'active']].max().reset_index()
#     covid_data_5 = covid_data_4[covid_data_4['Station Library Checkout'] == w_countries]

#     if w_countries:
#         zoom=2
#         zoom_lat = dict_of_locations[w_countries]['Lat']
#         zoom_long = dict_of_locations[w_countries]['Long']



#     return {
#         'data': [go.Scattermapbox(
#             lon=covid_data_5['Long'],
#             lat=covid_data_5['Lat'],
#             mode='markers',
#             marker=go.scattermapbox.Marker(size=covid_data_5['confirmed'] / 1500,
#                                            color=covid_data_5['confirmed'],
#                                            colorscale='HSV',
#                                            showscale=False,
#                                            sizemode='area',
#                                            opacity=0.3),
#             hoverinfo='text',
#             hovertext=
#             '<b>Country</b>: ' + covid_data_5['Station Library Checkout'].astype(str) + '<br>' +
#             '<b>Longitude</b>: ' + covid_data_5['Long'].astype(str) + '<br>' +
#             '<b>Latitude</b>: ' + covid_data_5['Lat'].astype(str) + '<br>' +
#             '<b>Confirmed Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_5['confirmed']] + '<br>' +
#             '<b>Death</b>: ' + [f'{x:,.0f}' for x in covid_data_5['death']] + '<br>' +
#             '<b>Recovered Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_5['recovered']] + '<br>' +
#             '<b>Active Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_5['active']] + '<br>'


#         )],

#         'layout': go.Layout(
#             hovermode='x',
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             margin=dict(r=0, l =0, b = 0, t = 0),
#             mapbox=dict(
#                 accesstoken='pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',
#                 center = go.layout.mapbox.Center(lat=zoom_lat, lon=zoom_long),
#                 style='dark',
#                 zoom=zoom,
#             ),
#             autosize=True



#         )
#     }

if __name__ == '__main__':
    app.run_server(debug=True)

