import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import plotly.express as px 
from dotenv import load_dotenv
import os

load_dotenv()

#HOST_REQUEST = "54.170.105.187"
HOST_REQUEST = os.getenv('HOST_REQUEST')
PORT_REQUEST = os.getenv('PORT_REQUEST')

def get_airlines_data(user, password, jour_depart, jour_arrive, delay=60):
    # Making a get request
    the_request = ""
    df = pd.DataFrame()
    df_final = pd.DataFrame()

    offset = 0
    while True:
        the_request = f"http://{HOST_REQUEST}:{PORT_REQUEST}/v1/airline-delays/LH?departure_date={jour_depart}&arrival_date={jour_arrive}&delay={delay}&limit=1000&offset={offset}"
        response = requests.get(the_request, auth = HTTPBasicAuth(user, password))
        
        if response.text != None and len(response.text) > 50:
            df = pd.read_json (response.text)
            df = df.drop('total', axis=1)
            df.dropna(axis=0, how="any", subset=None, inplace=True)
            offset += 1000
        else:
            break
        
        df_final = pd.concat([df_final,df])

    df_final[['arrivalActualTimeUtc', 'arrivalScheduledTimeUtc']] = df[['arrivalActualTimeUtc', 'arrivalScheduledTimeUtc']].astype('datetime64[ns]')
    df_final[['fspId', 'flightNumber']] = df[['fspId', 'flightNumber']].astype('int64')
    
    return df_final
 
def get_barchart(df_in, x_column, y_column, x_label, y_label):
    df_in = df_in.reset_index()
    df_compar_filter = df_in.sort_values(by= y_column, ascending=False)

    barchart = px.bar(
    data_frame=df_compar_filter,
    x=x_column,
    y=y_column,
    color = x_column, 
    opacity=0.9,
    text = y_column
    )
    barchart.update_layout(
    xaxis_title=None,
    yaxis_title=y_label,
    legend_title=None,
    font=dict(
    family="Courier New, monospace",
    size=18,
    color="RebeccaPurple"
    )
    )
    return barchart

def initial_graph(df_final, depart, arrivee):
    df_filter = df_final[ (df_final["departureAirport"]==depart) & (df_final["arrivalAirport"]==arrivee) ] 
    df_filter.reset_index()
    df_result  = df_filter[['startDateUtc','departureAirport', 'arrivalAirport']].groupby('startDateUtc').count()
    df_result.reset_index()
    
    figure1 =  get_barchart(df_result,  "startDateUtc" , "departureAirport","Date", "Nombre de vols")
    figure1.update(layout_showlegend=False)

    return figure1
