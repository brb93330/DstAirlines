import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Output,Input
from dash import html, Input, Output, ctx
import utils_dashboard as u
from dotenv import load_dotenv
import os

load_dotenv()

liste_choix_effectues={}

df_final = u.get_airlines_data(os.getenv('USER_API_NAME'),os.getenv('USER_API_PASSWORD'),os.getenv('DATE_DEPART_API'),os.getenv('DATE_ARRIVEE_API'), 60)

figure1 = u.initial_graph(df_final,os.getenv('DEFAULT_AEROPORT_DEPART'),os.getenv('DEFAULT_AEROPORT_ARRIVEE'))
liste_choix_effectues[os.getenv('DEFAULT_AEROPORT_DEPART')+os.getenv('DEFAULT_AEROPORT_ARRIVEE')+str(60)] = figure1

#u.list_avec_labels_et_valeurs(df_final["departureAirport"].unique(), )

app = dash.Dash(__name__, suppress_callback_exceptions=True)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id = 'page-content')
])


index_page = html.Div([
    html.H1('Statistiques des vols de la Lufthansa', style={'color' : 'blue', 'textAlign': 'center'}),
    html.Button(dcc.Link('Vols en retards', href='/delays'),style={'font-size': '20px','backgroundColor': 'beige', 'color':'white','width':'100%' , 'border':'1.5px black solid','height': '50px','text-align':'center', 'marginLeft': '20px', 'marginTop': 20}),
    html.Br(),
    html.Button(dcc.Link("Vols arrivés et annulés ", href='/compar_airlines'), style={'font-size': '20px','backgroundColor': 'beige', 'color':'white','width':'100%' , 'border':'1.5px black solid','height': '50px','text-align':'center', 'marginLeft': '20px', 'marginTop': 20}),
], style={'alignItems': 'center', 'verticalAlign':'middle'})


# Page n°1 pour la comparaison des joueurs
layout_1 = html.Div([
  html.H1("Vols en retards, ou à l'heure, entre 2 aéroports", style={'textAlign': 'center', 'color': 'blue'}),
  html.Br(),
  dbc.Label("Aéroport de départ", size="md"),
  html.Div(dcc.Dropdown(sorted(df_final["departureAirport"].unique()), placeholder = "Veuillez sélectionner un aéroport de départ", id = 'departureAirport-dropdown')),
  html.Br(),
  dbc.Label("Aéroport d'arrivée", size="md"),
  html.Div(dcc.Dropdown(sorted(df_final["arrivalAirport"].unique()), placeholder = "Veuillez sélectionner un aéroport d'arrivée", id = 'arrivalAirport-dropdown')),
  html.Br(),
  dcc.Graph(id='stats-vols-retard',figure=figure1),
  html.Br(),
  html.Label("Choisissez une durée de retard (en heures)", htmlFor="slider_1"),
  html.Div(dcc.Slider(id = 'slider_1',
                      min = 0,
                      max = 4,
                      step = 1)),
  html.Br(),
  html.Br(),
  html.Div(html.Button(dcc.Link('Revenir à la page de garde', href='/')), style = {'background' : 'white', 'color':'blue'}),
  html.Br(),
  html.Button('Rafraichir les données', id='btn-nclicks-1', n_clicks=0),

], style = {'background' : 'beige', 'color':'blue'})

@app.callback(Output(component_id='stats-vols-retard', component_property='figure'),
            [Input(component_id='departureAirport-dropdown', component_property='value'),Input(component_id='arrivalAirport-dropdown', component_property='value'),
             Input('slider_1', 'value'), Input('btn-nclicks-1', 'n_clicks') ],prevent_initial_call=True)
def update_graph(*args):
    to_reset = False
    if "btn-nclicks-1" == ctx.triggered_id:
        to_reset = True
        
    if to_reset:
        liste_choix_effectues.clear()

    delay=6
    if args[2]==None:
        delay=0
    else:
        delay=int(args[2]) * 60

    string_delay = str(delay)
    key = ""
    if (args[0] == None)  or (args[1] == None ):
        key = os.getenv('DEFAULT_AEROPORT_DEPART')+os.getenv('DEFAULT_AEROPORT_ARRIVEE')+str(60)
    else:
        key = args[0]+args[1]+string_delay
    
    if args[0]!= None and args[1]!= None and (key not in liste_choix_effectues):
        df_final = u.get_airlines_data(os.getenv('USER_API_NAME'),os.getenv('USER_API_PASSWORD'),os.getenv('DATE_DEPART_API'),os.getenv('DATE_ARRIVEE_API'), delay)
        df_filter = df_final[ (df_final["departureAirport"]==args[0]) & (df_final["arrivalAirport"]==args[1]) ] 
        df_filter.reset_index()
        df_result  = df_filter[['startDateUtc','departureAirport', 'arrivalAirport']].groupby('startDateUtc').count()
        df_result.reset_index()
        
        figure1 =  u.get_barchart(df_result,  "startDateUtc" , "departureAirport","Date", "Nombre de vols")

        figure1.update(layout_showlegend=False)
        liste_choix_effectues[key] = figure1
    
        return liste_choix_effectues[key]
    
    return liste_choix_effectues[key]


# Mise à jour de l'index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/delays':
        return layout_1
    elif pathname == '/compar_airlines':
        return layout_1
    else:
        return index_page




if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0', port = 5000)
    
