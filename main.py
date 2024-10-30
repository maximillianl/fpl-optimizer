from fpl_calculations import *
from optimizer import optimize_team

#main
raw_general_data = general_data()


# Prompt for budget input
budget_input = input("Enter your budget: ")

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
    budget_input = input("Enter your budget (default is 100): ")
    




formation_input = input("Enter your formation (#-#-#): ")
while True:
    try:
        formation = tuple(map(int, formation_input.split('-')))
        if sum(formation) == 10 and len(formation) == 3:
            break
        else:
            print("Formation must have 10 players.")
    except ValueError:
        if formation_input == '' or formation_input == None:
            formation = ''
            break
        else:
            print("Invalid input. Please enter a numeric value.")
            formation_input = input("Enter your formation (#-#-#): ")


    


if raw_general_data is not None:
    cleaned_general_data = prepare_data(raw_general_data)
    optimize_team(raw_general_data, budget, formation)
    
    print(calculations_gk(cleaned_general_data))
    print(calculations_def(cleaned_general_data))
    print(calculations_mid(cleaned_general_data))
    print(calculations_fwd(cleaned_general_data))

