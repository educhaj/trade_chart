import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px



df = pd.read_csv('Final_Ranks_01_24_2024.csv')

# Unique teams for dropdown
teams = df['Team'].unique()

# Dash app
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Player Salary and Value Comparison"),

    dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': team, 'value': team} for team in teams],
        multi=True,
        value=[teams[0], teams[1]],  # Initial team selection (choose 2 teams)
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='player-dropdown-team1',
        multi=True,
        style={'width': '50%'},
        value=[df[df['Team'] == teams[0]]['Name'].iloc[0]]  # Default to the first player in Team A
    ),

    dcc.Dropdown(
        id='player-dropdown-team2',
        multi=True,
        style={'width': '50%'},
        value=[df[df['Team'] == teams[1]]['Name'].iloc[0]]  # Default to the first player in Team B
    ),

    dcc.Graph(id='salary-bar'),
    dcc.Graph(id='dollar-value-bar'),
    dcc.Graph(id='overall-value-bar'),

    dash_table.DataTable(
        id='table-graph',
        columns=[{"name": col, "id": col} for col in df.columns],
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'fontFamily': 'Arial, sans-serif', 'fontSize': '14px'},
        style_header=dict(backgroundColor="orange"),
        style_data=dict(backgroundColor="white")
    )
])

# Callback to update player dropdowns, bar graphs, and table based on selected players and teams
@app.callback(
    [Output('player-dropdown-team1', 'options'),
     Output('player-dropdown-team2', 'options'),
     Output('salary-bar', 'figure'),
     Output('dollar-value-bar', 'figure'),
     Output('overall-value-bar', 'figure'),
     Output('table-graph', 'data')],
    [Input('team-dropdown', 'value'),
     Input('player-dropdown-team1', 'value'),
     Input('player-dropdown-team2', 'value')]
)
def update_content(selected_teams, selected_players_team1, selected_players_team2):
    if not selected_teams or not selected_players_team1 or not selected_players_team2:
        # Handle the case where some selections are empty
        return [], [], px.bar(), px.bar(), px.bar(), []

    filtered_df = df[
        ((df['Team'] == selected_teams[0]) & (df['Name'].isin(selected_players_team1))) |
        ((df['Team'] == selected_teams[1]) & (df['Name'].isin(selected_players_team2)))
    ]

    if filtered_df.empty:
        # Handle the case where the filtered DataFrame is empty
        return [], [], px.bar(), px.bar(), px.bar(), []

    # Update player dropdowns
    team1_players = df[df['Team'] == selected_teams[0]]['Name'].unique()
    team2_players = df[df['Team'] == selected_teams[1]]['Name'].unique()
    options_team1 = [{'label': player, 'value': player} for player in team1_players]
    options_team2 = [{'label': player, 'value': player} for player in team2_players]

    # Bar graphs
    salary_fig = px.bar(filtered_df, x='Team', y='Salary', color='Name', title='Player Salary Comparison')

    # Sum 'dollar_value' for each player
    summed_dollar_value = filtered_df.groupby('Team')['dollar_value'].sum().reset_index()

    # Bar graph for summed 'dollar_value'
    dollar_value_fig = px.bar(
        summed_dollar_value, x='Team', y='dollar_value', title='Summed Dollar Value')

    # Bar graph for Overall
    overall_fig = px.bar(filtered_df, x='Team', y='Overall_Value', color='Name', title='Player Overall Value Comparison')

    # DataTable
    table_data = filtered_df.to_dict('records')

    return options_team1, options_team2, salary_fig, dollar_value_fig, overall_fig, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
