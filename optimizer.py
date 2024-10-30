import pandas as pd
import numpy as np
import cvxpy as cp
from fpl_calculations import calculations_def, calculations_fwd, calculations_gk, calculations_mid


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
