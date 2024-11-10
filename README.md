# Fantasy Premier League Team Optimizer

## Overview

This project provides a tool to optimize Fantasy Premier League (FPL) teams using an integer optimization model. The goal is to select the best possible team of 11 players (including bench players) within a given budget, based on historical player performance data, team formation constraints, and the scoring system in FPL.

## Features
* **Player Selection**: Select players from four positions: Goalkeepers (GK), Defenders (DEF), Midfielders (MID), and Forwards (FWD).
* **Budget Management**: The optimizer selects a team within a specified budget for both starters and bench players.
* **Formation Constraints**: The optimizer allows you to specify a desired formation (3-5-2, 4-4-2, etc.), or it can automatically explore multiple formations to find the best team.
* **Value Score Calculation**: The optimizer uses historical performance data (goals, assists, clean sheets, etc.) to calculate value scores for each player and maximize the total score of the team.
* **Flexibility**: Users can input their desired budget and formation, or use default values.

## Setup
* **Get the Data**: The program fetches data from the Fantasy Premier League API, which includes player statistics and performance history. This data is processed to filter out unavailable, injured, or suspended players.
* **Player Data**: The optimizer uses detailed player statistics (e.g., points per game, minutes played, goals, assists) to give each player a value score.
* **Optimization**: The program uses a 0-1 integer optimization model (cvxpy) to maximize the total score of the team while adhering to the budget and formation constraints.

## Usage
### Step 1: Run the program
You can run the program directly from the command line or within a Python environment. The program will prompt you to input your budget and desired team formation. You can either enter a custom budget and formation or use the default values.

### Step 2: Enter Budget and Formation
The program will prompt you for:

* **Budget**: Enter a numeric value for your team budget (100.0). If no value is entered, the default budget is set to 100.0.
* **Formation**: Enter a formation in the format #-#-#, where:
  * The first number is the number of Defenders.
  * The second number is the number of Midfielders.
  * The third number is the number of Forwards.
  * The remaining players will be allocated to the bench, with a maximum of 4 bench players.
  * The formation must be a valid FPL formation
    * (3, 5, 2)
    * (3, 4, 3)
    * (4, 3, 3)
    * (4, 4, 2)
    * (4, 5, 1)
    * (5, 3, 2)
    * (5, 4, 1)

### Step 3: View Results
Once the optimization is completed, the program will output:
* **Best Formation**: The formation used (based on your budget and constraints).
* **Selected Players**: A list of the players chosen for the team, along with their positions, value scores, and prices.
* **Total Team Cost**: The total cost of the selected players.

### Step 4: See Players' Value Scores by Position
Once the optimized team is displayed, the program will ask if you would like to see the value scores of the players at a certain position
* **GK**: View the calculated scores for Goalkeepers.
* **DEF**: View the calculated scores for Defenders.
* **MID**: View the calculated scores for Midfielders.
* **FWD**: View the calculated scores for Forwards.
The program then prints the relevant player statistics for the selected position, showing a table of players along with their value scores and prices. This helps users analyze the individual performance metrics for each position before making further decisions for their Fantasy Premier League team.

## Code Breakdown
* **Data Collection**: The general_data() function fetches player data from the FPL API and filters out unavailable players.
* **Data Preparation**: The prepare_data() function prepares the data by selecting only relevant features for analysis.
* **Player Calculations**: Functions like calculations_gk(), calculations_def(), calculations_mid(), and calculations_fwd() calculate value scores for players based on their performance data.
* **Optimization**: The optimize_team() function uses cvxpy to solve a 0-1 integer optimization problem, maximizing the total team score under the constraints of budget and formation.

# Technologies and Methodologies
## Technologies Used
* **Python**: The primary programming language used to build this project, leveraging libraries for data processing, optimization, and visualization.
* **Pandas**: Utilized for data manipulation and processing of Fantasy Premier League (FPL) data.
* **NumPy**: Used for numerical calculations, including standard deviation and other mathematical operations.
* **cvxpy**: A library used for solving the optimization problem, specifically for 0-1 integer programming.
* **Requests**: To fetch real-time data from Fantasy Premier League’s public API.

## Methodology
* **Multi-Factor Model**: To calculate the value scores for players, a factor model was used, which is based on a combination of various player statistics and metrics. These factors include:
  * Player's Form
  * Player's Points
  * Players Price
  * Goals Scored
  * Assists
  * Clean Sheets
  * Expected Goals (xG) and Expected Assists (xA)
  * Minutes Played
  * Fixture Difficulty

These factors were weighted based on their importance to fantasy premier league performance. Each player's score was calculated by applying a weighted sum of these metrics, which helped generate a projected fantasy value based on current and historical performance.

The resulting scores were used as part of the optimization process to select the best team within the user’s budget constraints. The goal was to maximize the value score of the selected team, adhering to a formation structure.

* **Optimization with cvxpy**: The project uses convex optimization with the cvxpy library to solve the problem of team selection. The main objective is to:
1. Maximize the total value score of the selected players.
2. Ensure that the total cost of the selected team fits within the given budget.
3. Maintain the correct team formation, including constraints on the number of goalkeepers, defenders, midfielders, and forwards.
This approach allows for an efficient solution to the team selection problem, ensuring that the team has the best possible performance based on the selected scoring model, while adhering to the budget and formation constraints.

# Future Enhancements
* **Interactive GUI for Team Selection**: Implement a graphical representation of the team’s formation and provide an interactive way to input parameters (budget, formation).
* **Advanced Scoring Models/Projections**: Experiment with more advanced machine learning models to predict player performance based on historical data.
