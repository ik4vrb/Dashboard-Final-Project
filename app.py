# ! pip install dash_bootstrap_components

# import dependencies
import dash_bootstrap_components as dbc
import dash
from dash import Dash, dash_table, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from plotly.offline import init_notebook_mode, plot
import plotly as py
import plotly.graph_objs as go

# implement navbar with dropdowns and header
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Bar Graph", id="bar-graph-option"),
                dbc.DropdownMenuItem("Line Plot", id="line-plot-option"),
            ],
            nav=True,
            in_navbar=True,
            label="Graph Type",
        ),
    ],
    brand="Movie Data Viewer",
    brand_href="#",
    color="primary",
    dark=True,
)

# load the movies dataset into a pandas dataframe
df = pd.read_csv("data.csv")
df_topMovies = df.sort_values(by='gross', ascending=False)[:50]

# Get unique genres for dropdown options
df_genres = [{'label': genres, 'value': genres} for genres in df['genre'].unique()]
df_genres.insert(0, {'label': 'All', 'value': 'All'})

# Update line plot using plotly.express when callback is being used
#def update_graph(graph_type, selected_genre, selected_years):
#    filtered_df = df
#    if selected_genre != 'All':
#        filtered_df = filtered_df[filtered_df['genre'] == selected_genre]
#    filtered_df = filtered_df[filtered_df.year >= selected_years[0]]
#    filtered_df = filtered_df[filtered_df.year <= selected_years[1]]
#    df_topMovies = filtered_df.sort_values(by='gross', ascending=False)[:50]
#    if (graph_type == 'bar'):
#        trace1 = go.Bar(
#                x = df_topMovies['name'],
#                y = df_topMovies['gross'],
#                name = "Top Grossing Movies",
#                marker = dict(color = 'rgba(255, 174, 255, 0.5)',
#                             line=dict(color='rgb(0,0,0)',width=1.5)),
#                text = df_topMovies['genre'] + " " + (df_topMovies['rating']))
#        data = [trace1]
#        layout = go.Layout(barmode = "group")
#        fig = go.Figure(data = data, layout = layout)
#        return fig

# create trace1 to make a bar graph
trace1 = go.Bar(
                x = df_topMovies['name'],
                y = df_topMovies['gross'],
                name = "Top Grossing Movies",
                marker = dict(color = 'rgba(255, 174, 255, 0.5)',
                             line=dict(color='rgb(0,0,0)',width=1.5)),
                text = df_topMovies['genre'] + " " + (df_topMovies['rating']))
data = [trace1]
layout = go.Layout(barmode = "group", title='Top 50 - Highest Grossing Movies')
fig = go.Figure(data = data, layout = layout)
init_fig = fig

# initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

###LAYOUT###
# Layout defines container for nav bar, as well as a range slider, radio item selector, bar/line graph, and interactive data table
app.layout = html.Div(children=[
    dbc.Container(
    [navbar, dash.page_container],
    fluid = True),
    html.Div([
    html.H3(children="Timeline"),
    dcc.RangeSlider(
            id='year-slider',
            min=int(min(df['year'])),
            max=int(max(df['year'])),
            value=[int(min(df['year'])), int(max(df['year']))],
            marks={str(year): str(year) if year % 5 == 0 else '' for year in range(int(min(df['year'])), int(max(df['year'])) + 1)},
            tooltip={"placement": "bottom", "always_visible": True},
            step=1
        ),
    html.H3(children="Genre"),
    dcc.RadioItems(
    list(df_genres),
    'All',
    id='genres-radio',
    inline=True,
    labelStyle={'padding':'3px 5px 2px 5px'},
    inputStyle={'margin-right':'5px'}),
    html.H3(children="Graph of Highest Grossing Movies"),
    html.H5(children="You can select the graph type for this from the top-right dropdown."),
    html.Div(id='graph-container', children=[
            dcc.Graph(id='graph')
        ]), # dcc.Graph(id = 'bar-graph', figure=fig), # add bar/line graph
    dcc.Store(id='graph-type-store', data='bar')  # Store the graph type
    ]),
    html.Div([ # initialize datatable with necessary parameters
        html.H3(children="Score and Vote Analysis with Interactive Data Table"),
        dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.Div(id='datatable-interactivity-container') # graphs created from idt callbacks will be created here
    ])
])

# Define the initial content of the graph container
@app.callback(
    Output('graph-container', 'children'),
    [Input('bar-graph-option', 'n_clicks')],
    [Input('line-plot-option', 'n_clicks')],
    prevent_initial_call=True
)
def initial_graph(bar_clicks, line_clicks):
    return dcc.Graph(id='graph', figure=init_fig)

# Callback to update the stored graph type when a new option is clicked
@app.callback(
    Output('graph-type-store', 'data'),
    Input('bar-graph-option', 'n_clicks'),
    Input('line-plot-option', 'n_clicks'),
)
def update_graph_type(bar_clicks, line_clicks):
    ctx = dash.callback_context
    if ctx.triggered_id == 'bar-graph-option':
        return 'bar'
    elif ctx.triggered_id == 'line-plot-option':
        return 'line'
    else:
        return dash.no_update  # If no option is clicked, keep the current stored value

# Define callback for updating the graph with bar graph output for radio/slider inputs
@app.callback(
    Output('graph', 'figure'),
    Input('bar-graph-option', 'n_clicks'),
    Input('line-plot-option', 'n_clicks'),
    Input('genres-radio', 'value'),
    Input('year-slider', 'value'),
    State('graph-type-store', 'data'),  # Get the stored graph type
)

# Toggle graph callback function for when a graph type, year range, or genre has been selected
def toggle_graph(bar_clicks, line_clicks, selected_genre, selected_years, stored_graph_type):
    ctx = dash.callback_context # check for any context regarding graph type option chosen
    if ctx.triggered_id == 'bar-graph-option':
        graph_type = 'bar'
    elif ctx.triggered_id == 'line-plot-option':
        graph_type = 'line'
    else:
        graph_type = stored_graph_type  # Use stored graph type if no option is selected
    filtered_df = df # filter data set based off of range and genre selected
    if selected_genre != 'All':
        filtered_df = filtered_df[filtered_df['genre'] == selected_genre] 
    filtered_df = filtered_df[filtered_df.year >= selected_years[0]]
    filtered_df = filtered_df[filtered_df.year <= selected_years[1]]
    df_topMovies = filtered_df.sort_values(by='gross', ascending=False)[:50]
    if (graph_type == 'bar'): # create gross comparison bar graph
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
    if (graph_type == 'line'): # create gross comparison line graph
        trace1 = go.Scatter(
            x=df_topMovies['name'],
            y=df_topMovies['gross'],
            mode='lines+markers',
            name="Top Grossing Movies",
            marker=dict(color='rgba(255, 174, 255, 0.5)', line=dict(color='rgb(0,0,0)', width=1.5)),
            text=df_topMovies['genre'] + " " + (df_topMovies['rating'])
        )
        data = [trace1]
        layout = go.Layout(title='Top 50 - Highest Grossing Movies')
        fig = go.Figure(data=data, layout=layout)
        return fig
    
# Callback functions for interactive data table styles
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

# Callback functions for updating graphs under the data table
@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff['name'],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["score", "votes"] if column in dff
    ]

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
