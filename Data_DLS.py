import numpy as np
import pandas as pd
import json
#from pandas.json import json_normalize
import os

# Importing the Match data jsons.
filenames = []
for file in os.listdir('C:\Sophie Folder\Birkbeck\Project\Data\Ball by Ball ODIs Male'):
    filenames.append(os.path.join('C:\Sophie Folder\Birkbeck\Project\Data\Ball by Ball ODIs Male',file))

filenames[0:10]
len(filenames)

print(filenames[0])
print(filenames[0][62:])
type(filenames[0][62:])

# Create a column with match reference number from file
match_id = []
for f in filenames:
    match_id.append(f[62:-5])

print(match_id [0:10])
match_id_col = ['Match ID']
match_id = pd.DataFrame(match_id, columns = match_id_col)
match_id

# Read in all the match data
df = pd.DataFrame()
for file in filenames:
    with open(file) as f:
        d=json.load(f)
        d=pd.json_normalize(d, max_level=1)
    df = pd.concat([df,d])

#Have to normalize because the data types are different and otherwise you get error "Mixing dicts with non-Series may lead to ambiguous ordering"
df.head()
df = df.reset_index(drop=True)
df.head()
df = pd.concat([df,match_id], axis=1)
df.head()

# Drop any columns with meta in the name
df.drop(list(df.filter(regex = 'meta')), axis = 1, inplace = True)
df.head()

# Check whether different columns have any useful information or if they can be removed.  E.g. if every column is the same and there's no unique data then the column can likely be removed.
for col in df.columns:
    print(col)

df_filtered = df[df['info.balls_per_over']!=6]
df_filtered

df_filtered = df[df['info.gender']!='male']
df_filtered

df_filtered = df[df['info.match_type']!='ODI']
df_filtered

df['info.match_type_number'].duplicated().sum()

df_filtered = df[df['info.overs']!=50]
df_filtered

df_filtered = df[df['info.team_type']!='international']
df_filtered

df['info.venue'].isnull().sum()

for col in df.columns:
    print(col)

# Remove:
# balls per over is always 6, if so can remove as it adds no info.
# city as we have match ground elsewhere
# event as we have details of the teams and date elsewhere to identify which match
# gender as source data was all just mens matches
# match_type and match_type_number as neither are unique
# officials as not needed
# overs as not unique
# player_of_match, registry, season as not needed
# team_type as not unique
# teams not needed as we have them elsewhere
# toss not needed

clean_df=df.drop(columns=['info.balls_per_over',
                          'info.city',
                          'info.event',
                          'info.gender',
                          'info.match_type',
                          'info.match_type_number',
                          'info.officials',
                          'info.overs',
                          'info.player_of_match',
                          'info.registry',
                          'info.season',
                          'info.team_type',
                          'info.teams',
                          'info.toss'
                         ])

clean_df.head()

# Data has a column saying which column data is missing from
clean_df['info.missing']
clean_df[clean_df[['info.missing']].notnull().all(1)]

missing_list = []
for index, row in clean_df.iterrows():
    for miss in clean_df['info.missing']:
        missing_list.append(str(miss))

missing_set = set(missing_list)
len(missing_set)
missing_set

#convert info missing column into string
clean_df['info.missing'] = clean_df['info.missing'].apply(str)
clean_df[clean_df['info.missing'].str.contains("powerplays")]

# 2346 rows in total, 140 of those have missing powerplays.  6% dropped, is that okay?
# Remove the rows that are missing powerplay information

clean_df = clean_df[clean_df['info.missing'].str.contains("powerplays")==False]
clean_df.shape

# Other columns in missing not a problem as we're not using player of match or umpires and doesn't matter if the data is missing in that column as that actually means the data is complete
clean_df=clean_df.drop(columns=['info.missing'])
clean_df.shape

clean_df['info.dates'][951]


# Some rows have multiple dates, choose 1st as it's not relevant that its played over two/ three days
dates = clean_df['info.dates']

# Create a list of only start dates for the ODIs
start_dates = []
for i in dates:
    start_dates.append(i[0])

start_dates
len(start_dates)

# Create a dataframe from the list
start_date_df = pd.DataFrame(start_dates)
start_date_df.columns=['Start Date']
start_date_df

clean_df['info.dates'] = start_date_df['Start Date'].values

# Turning into date objects - just need to extract from list
start_date_df['Start Date']= pd.to_datetime(start_date_df['Start Date'])
start_date_df.shape
clean_df.shape
clean_df = clean_df.reset_index(drop=True)

# Add start dates to overall df (clean_df)
clean_df['Start Date'] = start_date_df['Start Date']
clean_df.shape
clean_df
clean_df['Start Date'][2201]

# Choose the ODIs from Jan 2002 and end of 2022
mask = (clean_df['Start Date'] >= pd.Timestamp('2001-12-31')) & (clean_df['Start Date'] < pd.Timestamp('2023-01-01'))
clean_df.loc[mask]
clean_df = clean_df.loc[mask]
clean_df.shape
clean_df=clean_df.drop(columns=['info.dates'])
clean_df.shape

supersubs = clean_df[clean_df[['info.supersubs']].notnull().all(1)]
supersubs.shape
supersubs

# Should I drop the supersubs?  Or should I try to incorporate with the main team.  Will initially drop and then see what we can do.
clean_df[clean_df['info.supersubs'].isna()]
clean_df = clean_df[clean_df['info.supersubs'].isna()]
clean_df=clean_df.drop(columns=['info.supersubs'])
clean_df

import pickle
pickle.dump(clean_df,open('dataset_level1.pkl','wb'))

matches = pickle.load(open('dataset_level1.pkl','rb'))
matches

# Use pickle so that you can search by the dictionary keys?
matches.iloc[0]
# https://www.kaggle.com/code/npspoofs/notebookbe117c4542
matches.iloc[0]['innings']

#working out how to access the different parts of the data
matches.iloc[0]['innings'][0]
matches.iloc[0]['innings'][0]['team']
len(matches.iloc[0]['innings'][0]['overs'])
matches = matches.reset_index(drop=True)
matches.iloc[0]['info.outcome']['winner']
matches.iloc[0]['info.outcome']['by']
matches.iloc[1]['info.outcome']['by']
matches.iloc[0]['info.players']['Australia']

#in a list so this gives us the 1st team's 1st over
#first number is the row number (i.e whole match) then column name innings, next number is innings number, then using keys to extract info
matches.iloc[0]['innings'][0]#['overs'][0]

#over with wickets
matches.iloc[0]['innings'][0]['overs'][4]['deliveries'][2]['wickets'][0]['player_out']
len(matches.iloc[0]['innings'][0]['overs'][0]['deliveries'])

#ball count iterating through each over?  And score count and score column
matches.iloc[0]['innings'][1]['overs'][0]['deliveries']
matches.iloc[0]['innings'][0]['overs'][0]['deliveries'][0]['runs']
matches.iloc[0]['innings'][0]['overs'][0]['deliveries'][0]['runs']['total']
matches.iloc[0]['innings'][0]['team']
matches.iloc[0]['innings'][1]['team']
len(matches.iloc[0]['innings'])
matches.iloc[0]['info.players']['Australia']
matches.iloc[0]['innings'][0]['powerplays']


innings = [0,1]
no_result = 0
no_powerplay = 0
dl = 0
delivery_df = pd.DataFrame()
for index, row in matches.iterrows():
    batting_team = []
    innings_num = []
    over_col = []
    ball_col = []
    match = []
    date = []
    runs = []
    running_total = []
    wickets_taken = []
    batter_out = []
    start_team = []
    remaining_team = []
    powerplays = []
    venue = []
    winner = []
    missing_result = []
    first_team_innings = []
    first_team_overandball = []
    remaining_over_col = []
    remaining_ball_col = []
    wickets_remaining = []
    extras=[]
    remainder=[]
    total_overs = []


    try:
        if row['info.outcome']['result']=='no result': 
            no_result+=1
            continue
        if row['info.outcome']['method'] == "D/L":
            dl+=1
            continue

    except KeyError:
        for num in innings:
            cumulative_runs = 0
            team = row['innings'][num]['team']
            starting_team = row['info.players'][team]
            current_team = starting_team.copy()
            wicket_count = 0


            for over in row['innings'][num]['overs']:
                ball_count = 0
                for ball in row['innings'][num]['overs'][over['over']]['deliveries']:

                    if 'extras' in ball:
                        if 'noballs' in ball['extras']:
                            extras.append("noballs")                            

                        elif 'wides' in ball['extras']:
                            extras.append("wides")

                        else:
                            ball_count+=1
                            extras.append("other")
                    else:
                        ball_count+=1
                        extras.append("N/E")

                    try:
                        powerplays.append(row['innings'][num]['powerplays'])
                    except KeyError:
                        no_powerplay+=1
                        powerplays.append('NP')                      

                    try:
                        batter_out.append(ball['wickets'][0]['player_out'])
                        if ball['wickets'][0]['kind'] != "retired hurt":
                            wicket_count+=1
                        current_team.remove(ball['wickets'][0]['player_out'])
                        #remove the player from the list current_team
                    except KeyError:
                        #no wicket
                        batter_out.append('NW')
                        pass

                    try:
                        winner.append(row['info.outcome']['winner']) 
                    except:
                        winner.append(row['info.outcome']['result'])

                    #ball_count needs to repeat if the ball had an extra?




                    batting_team.append(team)
                    innings_num.append(str(num+1))
                    over_col.append(over['over'])
                    match.append(row['Match ID'])
                    date.append(row['Start Date'])
                    ball_col.append(ball_count)
                    runs.append(ball['runs']['total'])
                    cumulative_runs+=ball['runs']['total']
                    running_total.append(cumulative_runs)
                    wickets_taken.append(wicket_count)
                    start_team.append(starting_team)
                    remaining_team.append(current_team.copy())                    
                    venue_list = [x.strip() for x in row['info.venue'].split(',')]
                    venue.append(venue_list)
                    remaining_over = 49-(over['over'])
                    remaining_ball = 6-ball_count
                    # There are 21 rows where ball count gets to 7 because there's 7 balls listed in the over in the original data.  
                    #No explanation as to why so assumption is that this is an error.  According to search this could be umpire error
                    if remaining_ball<0:
                        remaining_ball = 0
                    remaining_over_col.append(remaining_over)
                    remaining_ball_col.append(remaining_ball)

                    #happens when there's a wide or noball on 1st ball of over.  Number wouldn't be 
                    if remaining_ball ==6:
                        remainder.append(str(remaining_over +1))

                    #because the dl_df table doesn't have the remainder as 49.0 for example, it has it as 49
                    elif remaining_ball == 0:
                        remainder.append(str(remaining_over))
                    else:
                        remainder.append(str(remaining_over)+"."+str(remaining_ball)) 
                    wickets_remaining.append(str(10-wicket_count))

            for over in row['innings'][num]['overs']:
                for ball in row['innings'][num]['overs'][over['over']]['deliveries']:
                    if num == 0:
                        first_team_runs = running_total[-1]
                        first_team_innings.append("NaN")
                        first_team_overs = over_col[-1]
                        first_team_balls = ball_col[-1]
                        first_team_overandball.append("NaN")
                    else:
                        first_team_innings.append(first_team_runs)
                        first_team_overandball.append(first_team_overs+first_team_balls)






    loop_df = pd.DataFrame({'batting_team': batting_team, 'innings_num': innings_num, 'over_col': over_col, 'ball_col': ball_col, 'Match ID': match, 'Start Date': date, 'Runs': runs, 'Running Total': running_total, 'Batter out': batter_out, 'Wickets taken': wickets_taken, 'Start Team': start_team, 'Remaining Team': remaining_team, 'Powerplays': powerplays, 'Venue': venue, 'Winner': winner, 'First Team Innings': first_team_innings, 'Remaining Overs': remaining_over_col, 'Remaining Balls': remaining_ball_col, 'Remainder': remainder, 'Wickets Remaining': wickets_remaining, 'Extras': extras, 'Over and Balls Total': first_team_overandball})
    delivery_df = pd.concat([delivery_df,loop_df])

    #missing powerplay data for some row?

print(delivery_df)
print(len(delivery_df))
print(delivery_df.iloc[328])

first_team_overs
delivery_df['Over and Balls Total']
print(len(delivery_df))
print(delivery_df.iloc[328])

# Remaining ball in over more complex - may be more than 6 because of extras

# https://cricsheet.org/format/json/#delivery-data   
# https://en.wikipedia.org/wiki/Extra_(cricket)

# Do I need to make sure that first innings reached 50 therefore?

print(first_team_innings)

# Outcome can be:
# 
# result
# winner
# tie

print(delivery_df)

# Remove the 1st innings
delivery_df = delivery_df[delivery_df['innings_num'].str.contains("2")]

print(delivery_df)

delivery_df = delivery_df.reset_index(drop=True)

delivery_df[delivery_df['Extras'].str.contains('N/E')==True]
print(no_result)
print(dl)
print(no_powerplay)

#948066 where matches without powerplay information are removed

#df_filtered = df[df['info.balls_per_over']!=6]

no_powerplay_df = delivery_df[delivery_df['Powerplays']=='NP']
no_powerplay_df = no_powerplay_df[~no_powerplay_df.duplicated(subset=['Match ID'])].copy()

#Matches with missing powerplay data come from 2002 - 2005
no_powerplay_df['Start Date'].sort_values()

powerplay_df = delivery_df[delivery_df['Powerplays']!='NP']
powerplay_df = powerplay_df[~powerplay_df.duplicated(subset=['Match ID'])].copy()

powerplay_df.sort_values('Start Date', ascending=True)
powerplay_df = powerplay_df.reset_index(drop=True)

#Players.  Read in two sets of data - from ESPN cricketers data and Wikipedia
cricketers_df = pd.read_csv('Players.csv')
cricketers_df
cricketers_df = cricketers_df[['Full name', 'Playing role']]

cricketers_df = cricketers_df.dropna()
cricketers_df.rename(columns={'Full name': 'Name'}, inplace=True)
cricketers_df['Name']
cricketers_df[cricketers_df['Name'].str.contains("Coetzer")]

wiki_df = pd.read_csv('wiki_cricketers_csv')

frames = [cricketers_df, wiki_df]
long_cricketers_df = pd.concat(frames)
print(long_cricketers_df['Playing role'].unique())

long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Referee')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('referee')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Coach')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('coach')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('author')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Umpire')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('umpire')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Commentator')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Administrator')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('3rd man')==False ]
long_cricketers_df = long_cricketers_df[long_cricketers_df['Playing role'].str.contains('Anchor')==False ]


long_cricketers_df.drop_duplicates(inplace = True)

long_cricketers_df = long_cricketers_df.reset_index(drop=True)

long_cricketers_df = long_cricketers_df.assign(Value=None)

# value for players - work out how to create a column on it
# Start off with batters, if the phrase contains occasional then take the other role, then wicket keepers

for index, row in long_cricketers_df.iterrows():
    if 'Bat' in row['Playing role']:
        row['Value'] = 3
    elif 'bat' in row['Playing role']:
        row['Value'] = 3
    elif 'all' in row['Playing role']:
        row['Value'] = 2
    elif 'All' in row['Playing role']:
        row['Value'] = 2
    elif 'bowl' in row['Playing role']:
        row['Value'] = 1
    elif 'Bowl' in row['Playing role']:
        row['Value'] = 1
    elif 'Wicketkeeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicketkeeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket-keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicket-keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicket keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket Keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket-Keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket=keeper' in row['Playing role']:
        row['Value'] = 2
    elif '12th man' in row['Playing role']:
        row['Value'] = 1
    elif 'Field' in row['Playing role']:
        row['Value'] = 1
    elif 'spin' in row['Playing role']:
        row['Value'] = 1
    elif 'Spin' in row['Playing role']:
        row['Value'] = 1
    elif 'arm' in row['Playing role']:
        row['Value'] = 1

missing_rows = long_cricketers_df[long_cricketers_df.isna().any(axis=1)]
print(missing_rows)
print(missing_rows.shape)

#Where there are errors in the data - manually assign player role or delete row

long_cricketers_df.iloc[4266]['Playing role'] = 'Batter'
long_cricketers_df.iloc[4904]['Playing role'] = 'Batter'
long_cricketers_df.iloc[5004]['Playing role'] = 'All-rounder'
long_cricketers_df.iloc[5783]['Playing role'] = 'Batter'
long_cricketers_df.iloc[6072]['Playing role'] = 'Wicket-keeper'
long_cricketers_df.iloc[6073]['Playing role'] = 'Bowler'
long_cricketers_df.iloc[6212]['Playing role'] = 'Wicket-keeper'
long_cricketers_df.iloc[6538]['Playing role'] = 'Batter'
long_cricketers_df.iloc[6686]['Playing role'] = 'Bowler'
long_cricketers_df.iloc[7257]['Playing role'] = 'Batter'
long_cricketers_df.iloc[7543]['Playing role'] = 'Bowler'
long_cricketers_df.iloc[7949]['Playing role'] = 'Bowler'
long_cricketers_df.iloc[9174]['Playing role'] = 'Batter'
long_cricketers_df.iloc[9862]['Playing role'] = 'All-rounder'
long_cricketers_df.iloc[10245]['Playing role'] = 'Bowler'


long_cricketers_df=long_cricketers_df.drop(2752, axis=0) # number not name
long_cricketers_df=long_cricketers_df.drop(5222, axis=0) #incorrect info on Wikipedia
long_cricketers_df=long_cricketers_df.drop(6049, axis=0) #only 1 first class match

long_cricketers_df = long_cricketers_df.reset_index(drop=True)
missing_rows = long_cricketers_df[long_cricketers_df.isna().any(axis=1)]
missing_rows

#Run again now we know what's missing

for index, row in long_cricketers_df.iterrows():
    if 'Bat' in row['Playing role']:
        row['Value'] = 3
    elif 'bat' in row['Playing role']:
        row['Value'] = 3
    elif 'all' in row['Playing role']:
        row['Value'] = 2
    elif 'All' in row['Playing role']:
        row['Value'] = 2
    elif 'bowl' in row['Playing role']:
        row['Value'] = 1
    elif 'Bowl' in row['Playing role']:
        row['Value'] = 1
    elif 'Wicketkeeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicketkeeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket-keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicket-keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'wicket keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket Keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket-Keeper' in row['Playing role']:
        row['Value'] = 2
    elif 'Wicket=keeper' in row['Playing role']:
        row['Value'] = 2
    elif '12th man' in row['Playing role']:
        row['Value'] = 1
    elif 'Field' in row['Playing role']:
        row['Value'] = 1
    elif 'spin' in row['Playing role']:
        row['Value'] = 1
    elif 'Spin' in row['Playing role']:
        row['Value'] = 1
    elif 'arm' in row['Playing role']:
        row['Value'] = 1


missing_rows = long_cricketers_df[long_cricketers_df.isna().any(axis=1)]


long_cricketers_df.drop(['Playing role'], axis=1, inplace=True)

#Splitting names into first name, middle name etc, then taking the initials for all names but surnames and creating 

name_list = []
for index, row in long_cricketers_df.iterrows():
    name_list.append(row['Name'].split())

initial_name= []
for n in name_list:
    str = ''
    for i in range(0,len(n)):
        if i<len(n)-1:
            str+=n[i][0]
        if i == len(n)-1:
            str+=' '
            str+= n[i]
    initial_name.append(str)

print(initial_name)
initial_name_df = pd.DataFrame(initial_name)
print(initial_name_df)


long_cricketers_df
long_cricketers_df['I_Name'] = initial_name_df[0]

long_cricketers_df
long_cricketers_df[long_cricketers_df['Name'].str.contains("Codrington")]


full_name_dict = dict(zip(long_cricketers_df.Name, long_cricketers_df.Value))
print(full_name_dict)

initial_name_dict = dict(zip(long_cricketers_df.I_Name, long_cricketers_df.Value))
print(initial_name_dict)

full_name_dict.update(initial_name_dict)
full_name_dict['Z Haider']