import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd, datetime as dt




#Sök igenom projektmappen för att hitta alla .csv-filer som hämtats från request_csv-modulen
#Jämför träffarna med listan på filnamn för att rensa ut alla alternativ där en .csv-fil

df = pd.read_excel("register.xlsx")
df = df[df.status_code == 200]
df.reset_index(inplace=True)
print(df['status_code'])


#Hämtar en css-mall för webappen.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


app.layout = html.Div(children=[
    html.H1(children='Svenska flöden'),

    dcc.Dropdown(
        id='choice',
        options=[{'label': str(df.station_name[i] + ', ' + df.river_name[i]), 'value': df.station_number[i]} for i
                 in
                 range(len(df.index))],
        searchable=True
    ),

    dcc.Graph(
        id='graph',
        style={
            'height': 700,
            'width': 900,
            },
    )
],
style = {'margin':'auto','width': '50%'})

#En callback för att uppdatera grafen beroende på vilket alternativ som väljs i droplistan.
#Den efterföljande funktionen läser in csv-filen för det valda alternativet och hanterar all data för att göra det presentabelt.
@app.callback(
    Output('graph', 'figure'),
    [Input('choice', 'value')],
    )

def update_graph(station_number):

    # Url för att hämta data
    url_first_part = 'https://opendata-download-hydroobs.smhi.se/api/version/1.0/parameter/1/station/'
    url_second_part = '/period/corrected-archive/data.csv'
    url = url_first_part + str(station_number) + url_second_part

    # Import data and clean the file from junk, make 2 dataframes to be able to compare years
    df = pd.read_csv(url, sep=';', header=None, error_bad_lines=False, skiprows=20)
    df_temp = pd.read_csv(url, sep=';', header=None, error_bad_lines=False, skiprows=20)
    df = df.iloc[20:]
    df.drop(df.columns[[2, 3]], axis=1, inplace=True)

    #Rename columns
    df.columns = ['date', 'flow']

    #Set x-axis to datetime format and fetch the date of the last entry
    df['date'] = pd.to_datetime(df['date'])

    #Clean the second dataframe from junk
    df_temp = df_temp.iloc[20:]
    df_temp.drop(df_temp.columns[[2, 3]], axis=1, inplace=True)

    # Set x-axis to datetime format and fetch the date of the last entry of the second dataframe
    df_temp.columns = ['date', 'flow']
    df_temp['date'] = pd.to_datetime(df_temp['date'])
    df_temp.date = df_temp.date + dt.timedelta(days=365)

    x_max = df.date.max() + dt.timedelta(days=14)


    return {
        'data': [
            {'x': df.date, 'y': df.flow, 'type': 'line', 'name': 'Aktuellt datum'},
            {'x': df_temp.date, 'y': df.flow, 'type': 'line', 'name': 'Föregående år', 'line': {'color': 'red', 'dash': 'dash'}},
        ],
        'layout': {
            'title': str('Vattenföring i ' + str(station_number)),
            'xaxis': {'range': [x_max-dt.timedelta(days=379), x_max], 'title': 'Datum'},
            'yaxis': {'title': 'Vattenföring (m3/s)'},
            'legend': {'x': 0, 'y': 1}
        }

    }




if __name__ == '__main__':
    app.run_server(debug=True)