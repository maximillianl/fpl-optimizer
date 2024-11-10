from fpl_calculations import *
from optimizer import optimize_team

#main
raw_general_data = general_data()


# Prompt for budget input
budget_input = input("Enter your budget (default is 100.0): ")

# Initial check and validation
while True:
    try:
        # Try to convert input to float and check if it's a positive value
        budget = float(budget_input)
        if budget > 0:
            break
        else:
            print("Budget must be greater than 0.")
    except ValueError:
        if budget_input == '':
            budget = 100.0
            break
        else:
            print("Invalid input. Please enter a numeric value.")

    # Prompt again if input was invalid
    budget_input = input("Enter your budget (default is 100.0): ")
    


possible_formations = [
        (3, 5, 2),
        (3, 4, 3),
        (4, 3, 3),
        (4, 4, 2),
        (4, 5, 1),
        (5, 3, 2),
        (5, 4, 1),
    ]  

formation_input = input("Enter your formation (#-#-#) (Leave blank for optimal formation): ")
while True:
    try:
        formation = tuple(map(int, formation_input.split('-')))
        if sum(formation) == 10 and len(formation) == 3 and formation in possible_formations:
            break
        else:
            print("Formation must be a valid FPL formation and in the format #-#-#.")
    except ValueError:
        if formation_input == '' or formation_input == None:
            formation = ''
            break
        else:
            print("Invalid input. Please enter a numeric value.")
    formation_input = input("Enter your formation (#-#-#) (Leave blank for optimal formation): ")


    

if raw_general_data is not None:
    cleaned_general_data = prepare_data(raw_general_data)
    optimize_team(raw_general_data, budget, formation)
    
    while True:
        print("Enter the position for which you would like to see the value scores (GK, DEF, MID, FWD):")
        position_input = input("Type anything else to exit the program: ")
        position_input = position_input.upper()
        if position_input == 'GK':
            print(calculations_gk(cleaned_general_data))
        elif position_input == 'DEF':
            print(calculations_def(cleaned_general_data))
        elif position_input == 'MID':
            print(calculations_mid(cleaned_general_data))
        elif position_input == 'FWD':
            print(calculations_fwd(cleaned_general_data))
        else:
            break
    
