import requests
import json
import pandas as pd
from pandas import json_normalize
import seaborn as sns
import uuid
import ast
from sqlalchemy import create_engine

def first_value(lst):
    return lst[0]


# creating a list of the different pages of dungeons to use in the api
s3_dungeons = ['algethar-academy','brackenhide-hollow','halls-of-infusion','neltharus','ruby-life-pools','the-azure-vault','the-nokhud-offensive','uldaman-legacy-of-tyr']

# blank list to enter each api into based on their dungeon parameter
dungeons = []
# base api url
base_url = 'https://raider.io/api/v1/mythic-plus/runs'
# iterating through each dungeon in the s3_dungeons list to extrach the apis
for dungeon in s3_dungeons:
    # requesting api and inserting the current dungeon in the loop
    response = requests.get('https://raider.io/api/v1/mythic-plus/runs?season=season-df-4&region=world&dungeon={}&page=0'.format(dungeon))
   
    # checking to see that the api was successfully extracted
    if response.status_code == 200:
        data = response.json()
        # placing data from api into the dungeons list
        dungeons.append(data)    
    else:
        print(f"Error fetching data from page {page + 1}. Status code: {response.status_code}")


# checking the json file pulled from the api
dungeons

# flattening the api
df = pd.json_normalize(dungeons)

# taking out the rankings column, has all the data i need
rankings = df['rankings']

# flattening the rankings more into a dataframe and viewing how it's formatted
nr = json_normalize(rankings)

json_normalize(nr.loc[0])

# creating blank dataframe to concat all the dungeon data together into a single dataframe
full_df = pd.DataFrame()

# iterating each dungeon dataframe into a single dataframe
for dungeon in range(0,len(s3_dungeons)):
    current_dungeon = json_normalize(nr.loc[dungeon])
    full_df = pd.concat([full_df,current_dungeon])


# come back to 'run.roster' and 'run.weekly_modifiers'
# list of column names I want to drop
drop_col = ['run.keystone_team_id',
            'run.dungeon.type',
            'run.keystone_time_ms',
            'run.logged_run_id',
            'run.keystone_platoon_id',
            'run.dungeon.id',
            'run.dungeon.short_name',
            'run.dungeon.expansion_id',
            'run.status','run.videos',
            'run.num_modifiers_active',
            'run.faction',
            'run.deleted_at',
            'run.dungeon.num_bosses',
            'run.dungeon.group_finder_activity_ids',
            'run.platoon', 
            'run.dungeon.patch',
            'run.dungeon.icon_url',
            'run.dungeon.slug',
            'run.platoon.name',
            'run.platoon.slug',
            'run.platoon.short_name',
            'run.platoon.logo',
            'run.platoon.id',
            'run.dungeon.wowInstanceId',
            'run.dungeon.map_challenge_mode_id']

# dropping columns in the list
full_df = full_df.drop(drop_col, axis=1)
full_df.head()


# Cleaning columns names
full_df = full_df.rename(columns={'rank':'Rank',
                                  'score':'Score',
                                  'run.season':'Season',
                                  'run.dungeon.name':'Dungeon',
                                  'run.dungeon.keystone_timer_ms':'Key.Time',
                                  'run.keystone_run_id':'Key.Run.ID',
                                  'run.mythic_level':'Key.Level',
                                  'run.clear_time_ms':'Clear.Time',
                                  'run.completed_at':'Date.Completed',
                                  'run.num_chests':'Key.Upgrade',
                                  'run.time_remaining_ms':'Time.Left',
                                  'run.weekly_modifiers':'Affixes',
                                  'run.keystone_team_id':'Team',
                                  })




# cleaning season column to show current number only
full_df['Season'] = full_df['Season'].apply(lambda x:x[-1])
full_df['Season']


# converting date column to datetime and cleaning the format
full_df['Date.Completed'] = pd.to_datetime(full_df['Date.Completed'])
full_df['Date.Completed'] = full_df['Date.Completed'].dt.date
full_df['Date.Completed']


# changing several columns originally presented in ms to minutes with seconds
full_df['Clear.Time'] = pd.to_timedelta(full_df['Clear.Time'], unit='ms')
full_df['Clear.Time'] = round(full_df['Clear.Time'].dt.seconds / 60, 2)
full_df['Clear.Time']  


full_df['Key.Time'] = pd.to_timedelta(full_df['Key.Time'], unit='ms')
full_df['Key.Time'] = round(full_df['Key.Time'].dt.seconds / 60, 2)
full_df['Key.Time']


full_df['Time.Left'] = pd.to_timedelta(full_df['Time.Left'], unit='ms')
full_df['Time.Left'] = round(full_df['Time.Left'].dt.seconds / 60, 2)
full_df['Time.Left']


roster = json_normalize(full_df['run.roster'])
print(roster[0][0])
print(roster[2][0])

parties = {}
for index, party in roster.iterrows():
    row_list = party.tolist()
    parties[index] = row_list

traits_needed = ['role', 
                 'character.name', 
                 'character.class.name', 
                 'character.race.name', 
                 'character.spec.name', 
                 'character.region.short_name' 
                 ]

roles = []
names = []
class_name = []
race = []
spec = []
region = []


for party in parties.values():
    party_roles = []
    party_names = []
    party_class_names = []
    party_races = []
    party_specs = []
    party_regions = []
    for character_data in party:
        for key, value in character_data.items():
            if key in traits_needed:
                if key == 'role':
                    party_roles.append(value)
                elif key == 'character.name':
                    party_names.append(value)
                elif key == 'character.class.name':
                    party_class_names.append(value)
                elif key == 'character.race.name':
                    party_races.append(value)
                elif key == 'character.spec.name':
                    party_specs.append(value)
                elif key == 'character.region.short_name':
                    party_regions.append(value)

    # Append the lists for this party to the main lists
    roles.append(party_roles)
    names.append(party_names)
    class_name.append(party_class_names)
    race.append(party_races)
    spec.append(party_specs)
    region.append(party_regions)


full_df['roles'] = roles
full_df['names'] = names
full_df['class_name'] = class_name
full_df['race'] = race 
full_df['spec'] = spec
full_df['region'] = region
full_df['region'] = full_df['region'].apply(first_value)
full_df = full_df.drop(columns=['run.roster'])
full_df.head()



#df = full_df
#engine = create_engine("mysql+pymysql://root:Gulfstream2019!@localhost:3306/native_db", echo=False)
#df.to_sql('MDungeons', con=engine, index=False, if_exists='replace')

