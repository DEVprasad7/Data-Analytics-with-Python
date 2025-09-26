import pandas as pd
import os

data_folder = "Cleaned Data"
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
all_data = []

for year in years:
    file_path = f"{data_folder}/ipl_{year}_cleaned.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['year'] = year
        all_data.append(df)

# Combine all data
combined_df = pd.concat(all_data, ignore_index=True)

combined_df.to_csv("ipl_2018_2025_combined.csv", index=False)

print("=== IPL DATA ANALYSIS (2018-2025) ===\n")

print(f"Total matches: {len(combined_df)}")
print(f"Years covered: {sorted(combined_df['year'].unique())}")
print(f"Matches per year:")
print(combined_df['year'].value_counts().sort_index())


all_teams = set()
for col in ['first_inn_team', 'second_inn_team']:
    all_teams.update(combined_df[col].unique())

print(f"\nUnique teams: {len(all_teams)}")
print(f"Teams: {sorted(all_teams)}")

total_wins = {}
for _, row in combined_df.iterrows():
    result = row['match_result']
    if 'won' in result:
        if 'Match tied (' in result:
            # Extract winner from tied match format: "Match tied (TEAM won...)"
            winner = result.split('Match tied (')[1].split(' won')[0]
        else:
            # Regular win format: "TEAM won by..."
            winner = result.split(' won')[0]
        total_wins[winner] = total_wins.get(winner, 0) + 1

print(f"\nTotal wins by team:")
for team, wins in sorted(total_wins.items(), key=lambda x: x[1], reverse=True):
    print(f"{team}: {wins}")

# Calculate total losses
total_losses = {}
for _, row in combined_df.iterrows():
    result = row['match_result']
    if 'won' in result:
        if 'Match tied (' in result:
            # Extract winner from tied match format: "Match tied (TEAM won...)"
            winner = result.split('Match tied (')[1].split(' won')[0]
        else:
            # Regular win format: "TEAM won by..."
            winner = result.split(' won')[0]
        # Determine loser
        first_team = row['first_inn_team']
        second_team = row['second_inn_team']
        loser = second_team if winner == first_team else first_team
        total_losses[loser] = total_losses.get(loser, 0) + 1

print(f"\nTotal losses by team:")
for team, losses in sorted(total_losses.items(), key=lambda x: x[1], reverse=True):
    print(f"{team}: {losses}")

# Special matches
tied_matches = combined_df[combined_df['match_result'].str.contains('tied|Match tied', case=False, na=False)]
no_result_matches = combined_df[combined_df['match_result'].str.contains('No result|abandoned', case=False, na=False)]

print(f"\nSpecial matches:")
print(f"Tied matches: {len(tied_matches)}")
print(f"No result/abandoned: {len(no_result_matches)}")

# Calculate no result matches by team
no_result_dict = {team: 0 for team in all_teams}
for _, row in combined_df.iterrows():
    result = row['match_result']
    if 'no result' in result.lower() or 'abandoned' in result.lower():
        first_team = row['first_inn_team']
        second_team = row['second_inn_team']
        no_result_dict[first_team] += 1
        no_result_dict[second_team] += 1

print(f"\nNo result/tied matches by team:")
for team, count in sorted(no_result_dict.items(), key=lambda x: x[1], reverse=True):
    print(f"{team}: {count}")

# Calculate total matches played by team
total_matches_played = {}
for _, row in combined_df.iterrows():
    first_team = row['first_inn_team']
    second_team = row['second_inn_team']
    total_matches_played[first_team] = total_matches_played.get(first_team, 0) + 1
    total_matches_played[second_team] = total_matches_played.get(second_team, 0) + 1

print(f"\nTotal matches played by team:")
for team, matches in sorted(total_matches_played.items(), key=lambda x: x[1], reverse=True):
    print(f"{team}: {matches}")

def extract_score(score_str):
    try:
        return int(score_str.split('/')[0])
    except:
        return 0

combined_df['first_inn_runs'] = combined_df['first_inn_score'].apply(extract_score)
combined_df['second_inn_runs'] = combined_df['second_inn_score'].apply(extract_score)
combined_df['total_runs'] = combined_df['first_inn_runs'] + combined_df['second_inn_runs']

highest_scoring = combined_df.loc[combined_df['total_runs'].idxmax()]
print(f"\nHighest scoring match:")
print(f"Year: {highest_scoring['year']}")
print(f"Teams: {highest_scoring['first_inn_team']} vs {highest_scoring['second_inn_team']}")
print(f"Scores: {highest_scoring['first_inn_score']} vs {highest_scoring['second_inn_score']}")
print(f"Total runs: {highest_scoring['total_runs']}")

print(f"\nAverage runs per match: {combined_df['total_runs'].mean():.1f}")