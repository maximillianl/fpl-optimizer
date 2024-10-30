import requests
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
import cvxpy as cp




# get Individual Premier League Players
def general_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        data = pd.DataFrame(data["elements"])
        
        return data
    
    else:
        print("Error: ", response.status_code)
        return None


# preps data for calculations
def prepare_data(data):
    # data that only has useful to me info
    fpl = data[
            [
                'id',
                'first_name',
                'second_name',
                'web_name',
                'element_type',
                'form',
                'value_form',
                'points_per_game',
                'total_points',
                'minutes',
                'starts',
                'starts_per_90',
                'goals_scored',
                'assists',
                'expected_goals',
                'expected_assists',
                'expected_goal_involvements',
                'expected_goals_per_90',
                'expected_assists_per_90',
                'expected_goal_involvements_per_90',
                'clean_sheets',
                'goals_conceded',
                'goals_conceded_per_90',
                'clean_sheets_per_90',
                'saves',
                'saves_per_90',
                'dreamteam_count',
                'ep_next',
                'ep_this',
                'now_cost',
                'selected_by_percent',
                'status',
                'bonus',
                'team',
                'now_cost_rank_type',
                'form_rank_type',
                'points_per_game_rank_type',
                'event_points', #recent gw points
            ]
        ]
             
           
        # get rid of the 'u' 's' 'i' status players
        # "s": Suspended (due to red cards or accumulated yellow cards).
        # "u": Unavailable (might be due to personal reasons, transfer, or other unspecified reasons).
        # "i": Injured.
    fpl = fpl[fpl['status'] != 'u']
    fpl = fpl[fpl['status'] != 's']
    fpl = fpl[fpl['status'] != 'i']
    fpl = fpl.reset_index(drop=True)
    
    return fpl

 

#id me identifies the player's id based on their first name
def idme(data, first_name):
    print(first_name, (data.loc[data['first_name'] == first_name, ['id']]))
    return (data.loc[data['first_name'] == first_name, ['id']])



#--------------------------------------------------------------
#game by game data

def player_data(player_id):
    
    
    player_url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    
    player_response = requests.get(player_url)
    if player_response.status_code == 200:
        player_data = player_response.json()
        
        return prepare_player_data(player_data)
    
    # this check might have issues if it hits the else
    else:
        
        print("Error: ", player_response.status_code)
        return None, None
        



# leaves only useful game by game data
def prepare_player_data(player_data):
    fixtures = pd.DataFrame(player_data['fixtures'])
    history = pd.DataFrame(player_data['history'])

    fixtures = fixtures[['event', 'is_home', 'difficulty']]

    history = history[[
        'element', 'total_points', 'was_home', 'round', 'minutes',
       'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
       'saves', 'expected_goals', 'expected_assists',
       'expected_goal_involvements', 'value']
    ]
    
    fixtures.reset_index(drop=True)
    history.reset_index(drop=True)
    
    return fixtures, history
    
    
#--------------------------------------------------------------
#calculations


def calculations_gk(fpl_data):
    #only keep goalkeepers
    fpl_data = fpl_data[fpl_data['element_type'] == 1]
    fpl_data = fpl_data.reset_index(drop=True)
    
    
    names = []
    ids = []
    gkscores = []
    rank = []
    price = []
    
    # doesnt truncate results
    pd.set_option('display.max_rows', 200)  # adjust this as needed
    pd.set_option('display.max_columns', None)
    
    
    for i in range (len(fpl_data)):
        player_id = int(fpl_data.iloc[i]['id'])
        form = float(fpl_data.loc[fpl_data['id'] == player_id, 'form'].iloc[0])
        goals_conceded = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_conceded'].iloc[0])
        clean_sheets = float(fpl_data.loc[fpl_data['id'] == player_id, 'clean_sheets'].iloc[0])
        saves = float(fpl_data.loc[fpl_data['id'] == player_id, 'saves'].iloc[0])
        value_form = float(fpl_data.loc[fpl_data['id'] == player_id, 'value_form'].iloc[0])
        points_per_game = float(fpl_data.loc[fpl_data['id'] == player_id, 'points_per_game'].iloc[0])
        now_cost = float(fpl_data.loc[fpl_data['id'] == player_id, 'now_cost'].iloc[0])
        bonus = float(fpl_data.loc[fpl_data['id'] == player_id, 'bonus'].iloc[0])
        starts_per_90 = float(fpl_data.loc[fpl_data['id'] == player_id, 'starts_per_90'].iloc[0])
        
        
        games = 0
        
        fixtures,history = player_data(player_id)
        fixture1 = fixtures.loc[0, 'difficulty']
        fixture2 = fixtures.loc[1, 'difficulty']
        fixture3 = fixtures.loc[2, 'difficulty']
        fixture_difficulty = (fixture1 + fixture2 + fixture3) / 3
        points_to_price = points_per_game / (float(now_cost) / 10)
        
        #count number of games
        j = 0  # Start with i = 0

        while len(history) - j >= 0:
            games += 1 
            j += 1 


        if len(history)-1 >= 0:
            game1 = history.loc[len(history)-1, 'total_points']
            
        if len(history)-2 >= 0:
            game2 = history.loc[len(history)-2, 'total_points']
            
        if len(history)-3 >= 0:
            game3 = history.loc[len(history)-3, 'total_points']
            
        if len(history)-4 >= 0:
            game4 = history.loc[len(history)-4, 'total_points']
            
        if len(history)-5 >= 0:
            game5 = history.loc[len(history)-5, 'total_points']
            
        volatility = np.std([game1, game2, game3, game4, game5])
        
        #find per game
        clean_sheets_pg = clean_sheets/games
        saves_pg = saves/games
        goals_conceded_pg = goals_conceded/games
        bonus_pg = bonus/games
        
        #tries to use a factor model to give a point projection based on recent performance using scoring and most important stats
        GK_Score = ((.5 * value_form) + (.05 * points_per_game) + (.5 * points_to_price) + (.05 * form) + (1 * clean_sheets_pg) + (bonus_pg) + (0.4 * saves_pg) - (0.4 * goals_conceded_pg) - (0.1 * fixture_difficulty) - (0.05 * volatility) + (0.05 * starts_per_90))/2
        
        
        GK_Score = np.round(GK_Score, 2)
        names.append(fpl_data.loc[fpl_data['id'] == player_id, 'web_name'].iloc[0])
        ids.append(player_id)
        gkscores.append(GK_Score)
        rank.append(i+1)
        price.append(now_cost/10)
        
        
        goalkeeper_table = pd.DataFrame({
        'Rank': rank,
        'Name': names,
        'Score': gkscores,
        'ID': ids,
        'Price' : price,
        'Position' : 1
        })
    sorted_goalkeepers = goalkeeper_table.sort_values(by='Score', ascending=False)
    sorted_goalkeepers['Rank'] = range(1, len(goalkeeper_table) + 1)
    return sorted_goalkeepers

    



def calculations_def(fpl_data):
    #only keep defenders
    fpl_data = fpl_data[fpl_data['element_type'] == 2]
    fpl_data = fpl_data[fpl_data['total_points'] > 0]
    fpl_data = fpl_data.reset_index(drop=True)
     
    names = []
    ids = []
    defscores = []
    rank = []
    price = []
    
    
    #-----------------------------------------------------

    
    
    # idme(fpl_data, 'André')
    for i in range (len(fpl_data)):
        player_id = int(fpl_data.iloc[i]['id'])
        clean_sheets = float(fpl_data.loc[fpl_data['id'] == player_id, 'clean_sheets'].iloc[0])
        starts_per_90 = float(fpl_data.loc[fpl_data['id'] == player_id, 'starts_per_90'].iloc[0])
        goals_scored = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_scored'].iloc[0])
        assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'assists'].iloc[0])
        expected_goals = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_goals'].iloc[0])
        expected_assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_assists'].iloc[0])
        value_form = float(fpl_data.loc[fpl_data['id'] == player_id, 'value_form'].iloc[0])
        points_per_game = float(fpl_data.loc[fpl_data['id'] == player_id, 'points_per_game'].iloc[0])
        now_cost = float(fpl_data.loc[fpl_data['id'] == player_id, 'now_cost'].iloc[0])
        form = float(fpl_data.loc[fpl_data['id'] == player_id, 'form'].iloc[0])
        goals_conceded = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_conceded'].iloc[0])
        bonus = float(fpl_data.loc[fpl_data['id'] == player_id, 'bonus'].iloc[0])
        starts_per_90 = float(fpl_data.loc[fpl_data['id'] == player_id, 'starts_per_90'].iloc[0])

        fixtures,history = player_data(player_id)
        fixture1 = fixtures.loc[0, 'difficulty']
        fixture2 = fixtures.loc[1, 'difficulty']
        fixture3 = fixtures.loc[2, 'difficulty']
        fixture_difficulty = (fixture1 + fixture2 + fixture3) / 3
        points_to_price = points_per_game / (float(now_cost) / 10)
        
        j=0
        games = 0
        while len(history) - j >= 0:
            games += 1 
            j += 1 
        if games == 0:
            clean_sheets_pg = 0
            bonus_pg = 0
            goals_pg = 0
            assists_pg = 0
            expected_assists_pg = 0
            expected_goals_pg = 0
            goals_conceded_pg = 0
        else:
            clean_sheets_pg = clean_sheets/games
            bonus_pg = bonus/games
            goals_pg = goals_scored/games
            assists_pg = assists/games
            expected_assists_pg = expected_assists/games
            expected_goals_pg = expected_goals/games
            goals_conceded_pg = goals_conceded/games
        
        
        
        
        if len(history)-1 >= 0:
            game1 = history.loc[len(history)-1, 'total_points']
        if len(history)-2 >= 0:
            game2 = history.loc[len(history)-2, 'total_points']
        if len(history)-3 >= 0:
            game3 = history.loc[len(history)-3, 'total_points']
        if len(history)-4 >= 0:
            game4 = history.loc[len(history)-4, 'total_points']
        if len(history)-5 >= 0:
            game5 = history.loc[len(history)-5, 'total_points']
        volatility = np.std([game1, game2, game3, game4, game5])
        
              
        
        pd.set_option('display.max_rows', 200)  # Adjust this as needed
        pd.set_option('display.max_columns', None)

        DEF_Score = ((.4 * value_form) + (.05 * points_per_game) + (.3 * points_to_price) + (.05 * form) + (1 * clean_sheets_pg) + (bonus_pg) + (1.05 * goals_pg) + (.95 * assists_pg) + (.85 * expected_assists_pg) + (.95 * expected_goals_pg) - (.25 * goals_conceded_pg) - (0.1 * fixture_difficulty) - (0.05 * volatility) + (0.05 * starts_per_90))

       
        
        DEF_Score = np.round(DEF_Score, 2)
        names.append(fpl_data.loc[fpl_data['id'] == player_id, 'web_name'].iloc[0])
        ids.append(player_id)
        defscores.append(DEF_Score)
        rank.append(i+1)
        price.append(now_cost/10)
        
        
        def_table = pd.DataFrame({
        'Rank': rank,
        'Name': names,
        'Score': defscores,
        'ID': ids,
        'Price' : price,
        'Position' : 2
        })
    sorted_defenders = def_table.sort_values(by='Score', ascending=False)
    sorted_defenders['Rank'] = range(1, len(def_table) + 1)
    return sorted_defenders    
    
    
    
    
    
def calculations_mid(fpl_data):
    # only keep midfielders
    fpl_data = fpl_data[fpl_data['element_type'] == 3]
    fpl_data = fpl_data.reset_index(drop=True)
    
    names = []
    ids = []
    midscores = []
    rank = []
    price = []
    

    for i in range (len(fpl_data)):
        player_id = int(fpl_data.iloc[i]['id'])
        clean_sheets = float(fpl_data.loc[fpl_data['id'] == player_id, 'clean_sheets'].iloc[0])
        starts_per_90 = float(fpl_data.loc[fpl_data['id'] == player_id, 'starts_per_90'].iloc[0])
        goals_scored = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_scored'].iloc[0])
        assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'assists'].iloc[0])
        expected_goals = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_goals'].iloc[0])
        expected_assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_assists'].iloc[0])
        value_form = float(fpl_data.loc[fpl_data['id'] == player_id, 'value_form'].iloc[0])
        points_per_game = float(fpl_data.loc[fpl_data['id'] == player_id, 'points_per_game'].iloc[0])
        now_cost = float(fpl_data.loc[fpl_data['id'] == player_id, 'now_cost'].iloc[0])
        form = float(fpl_data.loc[fpl_data['id'] == player_id, 'form'].iloc[0])
        goals_conceded = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_conceded'].iloc[0])
        bonus = float(fpl_data.loc[fpl_data['id'] == player_id, 'bonus'].iloc[0])

        fixtures,history = player_data(player_id)
        fixture1 = fixtures.loc[0, 'difficulty']
        fixture2 = fixtures.loc[1, 'difficulty']
        fixture3 = fixtures.loc[2, 'difficulty']
        fixture_difficulty = (fixture1 + fixture2 + fixture3) / 3
        points_to_price = points_per_game / (float(now_cost) / 10)
        
        j=0
        games = 0
        while len(history) - j >= 0:
            games += 1 
            j += 1 
        if games == 0:
            clean_sheets_pg = 0
            bonus_pg = 0
            goals_pg = 0
            assists_pg = 0
            expected_assists_pg = 0
            expected_goals_pg = 0
        else:
            clean_sheets_pg = clean_sheets/games
            bonus_pg = bonus/games
            goals_pg = goals_scored/games
            assists_pg = assists/games
            expected_assists_pg = expected_assists/games
            expected_goals_pg = expected_goals/games
        
        
        # gets the std of the last 5 games for points and minutes
        if len(history)-1 >= 0:
            game1 = history.loc[len(history)-1, 'total_points']
        if len(history)-2 >= 0:
            game2 = history.loc[len(history)-2, 'total_points']
        if len(history)-3 >= 0:
            game3 = history.loc[len(history)-3, 'total_points']
        if len(history)-4 >= 0:
            game4 = history.loc[len(history)-4, 'total_points']
        if len(history)-5 >= 0:
            game5 = history.loc[len(history)-5, 'total_points']
        volatility = np.std([game1, game2, game3, game4, game5])
        
              
        
        pd.set_option('display.max_rows', None)  # adjust this as needed
        pd.set_option('display.max_columns', None)
                
        
        MID_Score = ((.4 * value_form) + (.05 * points_per_game) + (.3 * points_to_price) + (.1 * clean_sheets_pg) + (.05 * form) + (bonus_pg) + (1.1 * goals_pg) + (1 * assists_pg) + (.8 * expected_assists_pg) + (.9 * expected_goals_pg) - (0.1 * fixture_difficulty) - (0.05 * volatility) + (0.05 * starts_per_90))

        
        MID_Score = np.round(MID_Score, 2)
        names.append(fpl_data.loc[fpl_data['id'] == player_id, 'web_name'].iloc[0])
        ids.append(player_id)
        midscores.append(MID_Score)
        rank.append(i+1)
        price.append(now_cost/10)
        
        
        mid_table = pd.DataFrame({
        'Rank': rank,
        'Name': names,
        'Score': midscores,
        'ID': ids,
        'Price' : price,
        'Position' : 3
        })
    sorted_midfielders = mid_table.sort_values(by='Score', ascending=False)
    sorted_midfielders['Rank'] = range(1, len(mid_table) + 1)
    return sorted_midfielders

    
    
    
    
def calculations_fwd(fpl_data):
    # only keep forwards
    fpl_data = fpl_data[fpl_data['element_type'] == 4]
    fpl_data = fpl_data.reset_index(drop=True)
    
    names = []
    ids = []
    fwdscores = []
    rank = []
    price = []
    
    

    for i in range (len(fpl_data)):
        player_id = int(fpl_data.iloc[i]['id'])
        clean_sheets = float(fpl_data.loc[fpl_data['id'] == player_id, 'clean_sheets'].iloc[0])
        starts_per_90 = float(fpl_data.loc[fpl_data['id'] == player_id, 'starts_per_90'].iloc[0])
        goals_scored = float(fpl_data.loc[fpl_data['id'] == player_id, 'goals_scored'].iloc[0])
        assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'assists'].iloc[0])
        expected_goals = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_goals'].iloc[0])
        expected_assists = float(fpl_data.loc[fpl_data['id'] == player_id, 'expected_assists'].iloc[0])
        value_form = float(fpl_data.loc[fpl_data['id'] == player_id, 'value_form'].iloc[0])
        points_per_game = float(fpl_data.loc[fpl_data['id'] == player_id, 'points_per_game'].iloc[0])
        now_cost = float(fpl_data.loc[fpl_data['id'] == player_id, 'now_cost'].iloc[0])
        form = float(fpl_data.loc[fpl_data['id'] == player_id, 'form'].iloc[0])
        bonus = float(fpl_data.loc[fpl_data['id'] == player_id, 'bonus'].iloc[0])

        fixtures,history = player_data(player_id)
        fixture1 = fixtures.loc[0, 'difficulty']
        fixture2 = fixtures.loc[1, 'difficulty']
        fixture3 = fixtures.loc[2, 'difficulty']
        fixture_difficulty = (fixture1 + fixture2 + fixture3) / 3
        points_to_price = points_per_game / (float(now_cost) / 10)
        
        j=0
        games = 0
        while len(history) - j >= 0:
            games += 1 
            j += 1 
        if games == 0:
            clean_sheets_pg = 0
            bonus_pg = 0
            goals_pg = 0
            assists_pg = 0
            expected_assists_pg = 0
            expected_goals_pg = 0
        else:
            clean_sheets_pg = clean_sheets/games
            bonus_pg = bonus/games
            goals_pg = goals_scored/games
            assists_pg = assists/games
            expected_assists_pg = expected_assists/games
            expected_goals_pg = expected_goals/games
        
        
        
        
        # gets the std of the last 5 games for points and minutes
        if len(history)-1 >= 0:
            game1 = history.loc[len(history)-1, 'total_points']
        if len(history)-2 >= 0:
            game2 = history.loc[len(history)-2, 'total_points']
        if len(history)-3 >= 0:
            game3 = history.loc[len(history)-3, 'total_points']
        if len(history)-4 >= 0:
            game4 = history.loc[len(history)-4, 'total_points']
        if len(history)-5 >= 0:
            game5 = history.loc[len(history)-5, 'total_points']
        volatility = np.std([game1, game2, game3, game4, game5])
        
              
        
        pd.set_option('display.max_rows', 230)  # Adjust this as needed
        pd.set_option('display.max_columns', None)
        
        

        FWD_Score = ((.4 * value_form) + (.05 * points_per_game) + (.3 * points_to_price) + (.05 * form) + (bonus_pg) + (1.1 * goals_pg) + (1 * assists_pg) + (.8 * expected_assists_pg) + (.9 * expected_goals_pg) - (0.1 * fixture_difficulty) - (0.05 * volatility) + (0.05 * starts_per_90))

        FWD_Score = np.round(FWD_Score, 2)
        names.append(fpl_data.loc[fpl_data['id'] == player_id, 'web_name'].iloc[0])
        ids.append(player_id)
        fwdscores.append(FWD_Score)
        rank.append(i+1)
        price.append(now_cost/10)
        
        
        fwd_table = pd.DataFrame({
        'Rank': rank,
        'Name': names,
        'Score': fwdscores,
        'ID': ids,
        'Price' : price,
        'Position' : 4
        })
    sorted_forwards = fwd_table.sort_values(by='Score', ascending=False)
    sorted_forwards['Rank'] = range(1, len(fwd_table) + 1)
    return sorted_forwards


#--------------------------------------------------------------
# optimize full team using 0-1 integer optimization model 
def optimize_team(fpl_data, budget, formation):
    
    pd.set_option('display.max_rows', None)  # Adjust this as needed
    pd.set_option('display.max_columns', None)
    
    #combines the tables of scores for each position
    all_players = combine_scores(calculations_gk(fpl_data), calculations_def(fpl_data), calculations_mid(fpl_data), calculations_fwd(fpl_data))
    
    prices = all_players['Price'].values
    
    scores = all_players['Score'].values

    # number of decision variables
    num_dec = len(all_players)
    
    #set decision to 0 or 1 (binary)
    selection = cp.Variable(num_dec, boolean=True)
    
    #sets objective to be to maximize projected points
    objective = cp.Maximize(selection @ scores)
    
    #initiallizing best score
    best_score = 0
    
    # sents budget for starters and bench (16.9 for bench)
    starter_budget = budget-16.9
    
    bench_budget = 16.9
    
    possible_formations = [
        (3, 5, 2),
        (3, 4, 3),
        (4, 3, 3),
        (4, 4, 2),
        (4, 5, 1),
        (5, 3, 2),
        (5, 4, 1),
    ]    
    
    if formation is None or len(formation) == 0:
        for formations in possible_formations:
            constraints = [
                cp.sum(cp.multiply(prices, selection)) <= starter_budget,
                cp.sum(selection) == 11,  # Total players
                cp.sum(selection[all_players['Position'] == 1]) == 1,  # Goalkeepers
                cp.sum(selection[all_players['Position'] == 2]) == formations[0],  # Defenders
                cp.sum(selection[all_players['Position'] == 3]) == formations[1],  # Midfielders
                cp.sum(selection[all_players['Position'] == 4]) == formations[2],  # Forwards
            ]

            # Define and solve the problem
            problem = cp.Problem(objective, constraints)
            problem.solve()
            

            # Get the score of the selected players
            selected_players = all_players[selection.value > 0.5]
            
            total_score = sum(selected_players['Score'])

            # If this formation gives a better score, save it
            print("total score: ", total_score, ": best score: ", best_score)
            if total_score > best_score:
                best_score = total_score
                best_formation = formations
                best_players = selected_players

        # Print the best formation and players for just the starters
        print("Best Formation:", best_formation)
        
        bench_d = 5 - best_formation[0]
        bench_m = 5 - best_formation[1]
        bench_f = 3 - best_formation[2]
        
        
        
        constraints = [
            cp.sum(cp.multiply(prices, selection)) <= bench_budget,
            cp.sum(selection) == 4,  # Total players
            cp.sum(selection[all_players['Position'] == 1]) == 1,  # Goalkeepers
            cp.sum(selection[all_players['Position'] == 2]) == bench_d,  # Defenders
            cp.sum(selection[all_players['Position'] == 3]) == bench_m,  # Midfielders
            cp.sum(selection[all_players['Position'] == 4]) == bench_f,  # Forwards
        ]
        
        #define and solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        
        # Interpret results
        selected_bench = all_players[selection.value > 0.5]
        
        
        team = pd.concat([best_players[['Name', 'Position', 'Score', 'Price']], selected_bench[['Name', 'Position', 'Score', 'Price']]])
        
        print(team[['Name', 'Position', 'Score', 'Price']])
        print(sum(team['Price']))

    
    else:
        constraints = [
            cp.sum(cp.multiply(prices, selection)) <= starter_budget,
            cp.sum(selection) == 11,  # Total players
            cp.sum(selection[all_players['Position'] == 1]) == 1,  # Goalkeepers
            cp.sum(selection[all_players['Position'] == 2]) == formation[0],  # Defenders
            cp.sum(selection[all_players['Position'] == 3]) == formation[1],  # Midfielders
            cp.sum(selection[all_players['Position'] == 4]) == formation[2],  # Forwards
        ]

        
    
    
        #define and solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        
        # Interpret results
        selected_players = all_players[selection.value > 0.5]
        
        
        
        bench_d = 5 - formation[0]
        bench_m = 5 - formation[1]
        bench_f = 3 - formation[2]
        
        constraints = [
            cp.sum(cp.multiply(prices, selection)) <= bench_budget,
            cp.sum(selection) == 4,  # Total players
            cp.sum(selection[all_players['Position'] == 1]) == 1,  # Goalkeepers
            cp.sum(selection[all_players['Position'] == 2]) == bench_d,  # Defenders
            cp.sum(selection[all_players['Position'] == 3]) == bench_m,  # Midfielders
            cp.sum(selection[all_players['Position'] == 4]) == bench_f,  # Forwards
        ]
        
        #define and solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        
        # Interpret results
        selected_bench = all_players[selection.value > 0.5]
        
        
        team = pd.concat([selected_players[['Name', 'Position', 'Score', 'Price']], selected_bench[['Name', 'Position', 'Score', 'Price']]])
        
        print("Formation: ", formation)
        print(team[['Name', 'Position', 'Score', 'Price']])
        print(sum(team['Price']))
        return team
        
    
    
    
    
    
# combines the tables of scores for each position
def combine_scores(gk_table, def_table, mid_table, fwd_table):
    all_players = pd.concat([gk_table, def_table, mid_table, fwd_table], ignore_index=True)
    return all_players

