# ! pip install dash_bootstrap_components

# import dependencies
import dash_bootstrap_components as dbc
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from plotly.offline import init_notebook_mode, plot
import plotly as py
import plotly.graph_objs as go

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    color="primary",
    dark=True,
)

# load the movies dataset into a pandas dataframe
df = pd.read_csv("data.csv")
df_topMovies = df.sort_values(by='gross', ascending=False)[:50]

# Get unique genres for dropdown options
df_genres = [{'label': genres, 'value': genres} for genres in df['genre'].unique()]
df_genres.insert(0, {'label': 'All', 'value': 'All'});

# Update line plot using plotly.express when callback is being used
def update_graph(selected_genre, selected_years):
    filtered_df = df
    if selected_genre != 'All':
        filtered_df = filtered_df[filtered_df['genre'] == selected_genre]
    filtered_df = filtered_df[filtered_df.year >= selected_years[0]]
    filtered_df = filtered_df[filtered_df.year <= selected_years[1]]
    df_topMovies = filtered_df.sort_values(by='gross', ascending=False)[:50]
    trace1 = go.Bar(
                x = df_topMovies['name'],
                y = df_topMovies['gross'],
                name = "Top Grossing Movies",
                marker = dict(color = 'rgba(255, 174, 255, 0.5)',
                             line=dict(color='rgb(0,0,0)',width=1.5)),
                text = df_topMovies['genre'] + " " + (df_topMovies['rating']))
    data = [trace1]
    layout = go.Layout(barmode = "group")
    fig = go.Figure(data = data, layout = layout)
    return fig

# create trace1 
trace1 = go.Bar(
                x = df_topMovies['name'],
                y = df_topMovies['gross'],
                name = "Top Grossing Movies",
                marker = dict(color = 'rgba(255, 174, 255, 0.5)',
                             line=dict(color='rgb(0,0,0)',width=1.5)),
                text = df_topMovies['genre'] + " " + (df_topMovies['rating']))
data = [trace1]
layout = go.Layout(barmode = "group")
fig = go.Figure(data = data, layout = layout)

# initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

###LAYOUT###
# write a layout with a header 1 that "Fruit Inventory"

app.layout = html.Div(children=[
    dbc.Container(
    [navbar, dash.page_container],
    fluid = True),
    dcc.RangeSlider(
            id='year-slider',
            min=int(min(df['year'])),
            max=int(max(df['year'])),
            value=[int(min(df['year'])), int(max(df['year']))],
            marks={str(year): str(year) if year % 2 == 0 else '' for year in range(int(min(df['year'])), int(max(df['year'])) + 1)},
            tooltip={"placement": "bottom", "always_visible": True},
            step=1
        ),
    dcc.RadioItems(
    list(df_genres),
    'All',
    id='genres-radio',
    inline=True,
    labelStyle={'padding':'3px 5px 2px 5px'},
    inputStyle={'margin-right':'5px'}),
    dcc.Graph(id = 'bar-graph', figure=fig), # add bar graph
])

# Define callback for updating the graph
@app.callback(
    Output('bar-graph', 'figure'),
     [Input('genres-radio', 'value'),
     Input('year-slider', 'value')]
)
def update_graph_callback(selected_genre, selected_years):
    return update_graph(selected_genre, selected_years)

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
