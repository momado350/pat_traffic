# app env = myenv (source activate myenv)
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd



# url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
# url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
# url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
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



# Converting date column from string to proper date format
mer_df['Trans Hist Date'] = pd.to_datetime(mer_df['Trans Hist Date'])


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('lib_logo.png'),
                     id='corona-image',
                     style={
                         "height": "60px",
                         "width": "auto",
                         "margin-bottom": "25px",
                     },
                     )
        ],
            className="one-third column",
        ),
            
        html.Div([
            html.Div([
                html.H3("Patrons Traffic", style={"margin-bottom": "0px", 'color': 'white'}),
                html.H5("Track Patron Traffic by Library Branch", style={"margin-top": "0px", 'color': 'white'}),
                html.P("Traffic is counted based on circulation and Computer Usage. ", style={"margin-top": "0px", 'color': 'white'}),
            ])
        ], className="one-half column", id="title"),

        html.Div([
            html.H6('Last Updated: ' + str(mer_df['Trans Hist Date'].iloc[-1].strftime("%B %d, %Y")) + '  00:01 (UTC)',
                    style={'color': 'orange'}),

        ], className="one-third column", id='title1'),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

html.Div([
        html.Div([


            html.P('Select Branch', className = 'fix_label', style = {'color': 'white', 'margin-top': '2px'}),
            dcc.Dropdown(id = 'w_countries',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         value = 'all_values',
                         placeholder = 'Select branch',
                         options = [{'label': c, 'value': c}
                                    for c in (mer_df['Station Library Checkout'].unique())] + [{'label': 'SELECT ALL', 'value': 'all_values'}]
                                 
                                    , className = 'dcc_compon'),
                                


            ],
            className = "create_container2 four columns", style = {'margin-bottom': '20px', "margin-top": "20px"}),

    ], className = "row flex-display"),

html.Div([
         html.Div([
              html.Div(id='live_text1'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),


         html.Div([
              html.Div(id='live_text2'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text3'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),


         html.Div([
              html.Div(id='live_text4'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text5'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text6'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

    ], className = "row flex-display"),

    ], id="mainContainer",
    style={"display": "flex", "flex-direction": "column"})

@app.callback(
    Output('live_text1', 'children'),
    [
        Input('w_countries', 'value')
    ]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons = mer_df.groupby(['Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_patron = patrons['total'].iloc[-1]
        today_patron = patrons['total'].iloc[-1] - patrons['total'].iloc[-2]
    else:
        patrons = mer_df.groupby(['Trans Hist Date', 'Station Library Checkout'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_patron = patrons[patrons['Station Library Checkout'] == w_countries]['total'].iloc[-1] 
        today_patron = patrons[patrons['Station Library Checkout'] == w_countries]['total'].iloc[-1] - patrons[patrons['Station Library Checkout'] == w_countries]['total'].iloc[-2]

    
    
    
    #today_patron1 = patrons1[['total'].iloc[-1] - patrons1[['total'].iloc[-2]



    return [
               html.H6(children = "Yesterday's Total",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_patron),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
                    #   html.P('{0:,.0f}'.format(total_patron1),
                    #   style={'textAlign': 'center',
                    #          'color': 'orange',
                    #          'fontSize': 40}
                    #   ),
               html.P('Yesterday:  ' + ' ' + '{0:,.0f}'.format(today_patron)
                      + ' (' + str(round(((today_patron) / total_patron) * 100, 2)) + '%' + ' ' + 'vs day before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text2', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons = mer_df.groupby(['Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_computer = patrons['SessionID'].iloc[-1]
        today_computer = patrons['SessionID'].iloc[-1] - patrons['SessionID'].iloc[-2]
    else:
        patrons = mer_df.groupby(['Trans Hist Date', 'Station Library Checkout'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_computer = patrons[patrons['Station Library Checkout'] == w_countries]['SessionID'].iloc[-1]
        today_computer = patrons[patrons['Station Library Checkout'] == w_countries]['SessionID'].iloc[-1] - patrons[patrons['Station Library Checkout'] == w_countries]['SessionID'].iloc[-2]



    return [
               html.H6(children = "Yesterday's Computer",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_computer),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Yeterday:  ' + ' ' + '{0:,.0f}'.format(today_computer)
                      + ' (' + str(round(((today_computer) / total_computer) * 100, 2)) + '%' + ' ' + 'vs day before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text3', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons = mer_df.groupby(['Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_criculation = patrons['patrons'].iloc[-1]
        today_circulation = patrons['patrons'].iloc[-1] - patrons['patrons'].iloc[-2]
    else:
        patrons = mer_df.groupby(['Trans Hist Date', 'Station Library Checkout'])[['patrons', 'SessionID', 'total']].sum().reset_index()
        total_criculation = patrons[patrons['Station Library Checkout'] == w_countries]['patrons'].iloc[-1]
        today_circulation = patrons[patrons['Station Library Checkout'] == w_countries]['patrons'].iloc[-1] - patrons[patrons['Station Library Checkout'] == w_countries]['patrons'].iloc[-2]



    return [
               html.H6(children = "Yesterday's Circulation",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_criculation),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Yesterday:  ' + ' ' + '{0:,.0f}'.format(today_circulation)
                      + ' (' + str(round(((today_circulation) / total_criculation) * 100, 2)) + '%' + ' ' + 'vs day before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text4', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons1 = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_total = patrons1['total'].iloc[-2]
        week_total_dif = patrons1['total'].iloc[-2] - patrons1['total'].iloc[-3]
    else:
        patrons1 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_total = patrons1[patrons1['Station Library Checkout'] == w_countries]['total'].iloc[-2]
        week_total_dif = patrons1[patrons1['Station Library Checkout'] == w_countries]['total'].iloc[-2] - patrons1[patrons1['Station Library Checkout'] == w_countries]['total'].iloc[-3]



    return [
               html.H6(children = "Week Total",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(weekly_total),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Last Week:  ' + ' ' + '{0:,.0f}'.format(week_total_dif)
                      + ' (' + str(round(((week_total_dif) / weekly_total) * 100, 2)) + '%' + ' ' + 'vs Week before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text5', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons1 = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_Computer = patrons1['SessionID'].iloc[-2]
        week_computer_dif = patrons1['SessionID'].iloc[-2] - patrons1['SessionID'].iloc[-3]
    else:
        patrons1 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_Computer = patrons1[patrons1['Station Library Checkout'] == w_countries]['SessionID'].iloc[-2]
        week_computer_dif = patrons1[patrons1['Station Library Checkout'] == w_countries]['SessionID'].iloc[-2] - patrons1[patrons1['Station Library Checkout'] == w_countries]['SessionID'].iloc[-3]




    return [
               html.H6(children = "Weekly Computer Users",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(weekly_Computer),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Last Week:  ' + ' ' + '{0:,.0f}'.format(week_computer_dif)
                      + ' (' + str(round(((week_computer_dif) / weekly_Computer) * 100, 2)) + '%' + ' ' + 'vs Week before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text6', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    if w_countries == 'all_values':
        patrons1 = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_circulation = patrons1['patrons'].iloc[-2]
        week_circulation_dif = patrons1['patrons'].iloc[-2] - patrons1['patrons'].iloc[-3]
    else:
        patrons1 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='1W')])[['patrons', 'SessionID', 'total']].sum().reset_index()
        weekly_circulation = patrons1[patrons1['Station Library Checkout'] == w_countries]['patrons'].iloc[-2]
        week_circulation_dif = patrons1[patrons1['Station Library Checkout'] == w_countries]['patrons'].iloc[-2] - patrons1[patrons1['Station Library Checkout'] == w_countries]['patrons'].iloc[-3]




    return [
               html.H6(children = "Weekly Circulation Users",
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(weekly_circulation),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Last Week:  ' + ' ' + '{0:,.0f}'.format(week_circulation_dif)
                      + ' (' + str(round(((week_circulation_dif) / weekly_circulation) * 100, 2)) + '%' + ' ' + 'vs Week before)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )
    ]



if __name__ == '__main__':
    app.run_server(debug=True)