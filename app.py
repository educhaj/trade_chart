import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px



df = pd.read_csv('Final_ranks.csv')

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
    dcc.Graph(id='value-bar'),
    dcc.Graph(id='overall-value-bar'),

])

# Callback to update player dropdowns based on selected teams
@app.callback(
    [Output('player-dropdown-team1', 'options'),
     Output('player-dropdown-team2', 'options')],
    [Input('team-dropdown', 'value')]
)
def update_player_dropdowns(selected_teams):
    if selected_teams is None or len(selected_teams) < 2:
        # Handle the case where less than two teams are selected
        return [], []

    team1_players = df[df['Team'] == selected_teams[0]]['Name'].unique()
    team2_players = df[df['Team'] == selected_teams[1]]['Name'].unique()

    options_team1 = [{'label': player, 'value': player} for player in team1_players]
    options_team2 = [{'label': player, 'value': player} for player in team2_players]

    return options_team1, options_team2

# Callback to update bar graphs based on selected players and teams
@app.callback(
    [Output('salary-bar', 'figure'),
     Output('value-bar', 'figure'),
    Output('overall-value-bar', 'figure')],
    [Input('team-dropdown', 'value'),
     Input('player-dropdown-team1', 'value'),
     Input('player-dropdown-team2', 'value')]
)
def update_bar_graphs(selected_teams, selected_players_team1, selected_players_team2):
    if not selected_teams or not selected_players_team1 or not selected_players_team2:
        # Handle the case where some selections are empty
        return px.bar(), px.bar()

    filtered_df = df[((df['Team'] == selected_teams[0]) & (df['Name'].isin(selected_players_team1))) |
                     ((df['Team'] == selected_teams[1]) & (df['Name'].isin(selected_players_team2)))]

    if filtered_df.empty:
        # Handle the case where the filtered DataFrame is empty
        return px.bar(), px.bar()

    # Bar graph for salary
    salary_fig = px.bar(filtered_df, x='Team', y='Salary', color='Name', title='Player Salary Comparison')


   # Sum 'dollar_value' for each player
    summed_dollar_value = filtered_df.groupby('Team')['dollar_value'].sum().reset_index()

    # Bar graph for summed 'dollar_value'
    dollar_value_fig = px.bar(
        summed_dollar_value, x='Team', y='dollar_value', title='Summed Dollar Value')

    #     # Bar graph for Overall
    overall_fig = px.bar(filtered_df, x='Team', y='Overall_Value',color = 'Name', title='Player Overall Value Comparison')



    return salary_fig, dollar_value_fig, overall_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
