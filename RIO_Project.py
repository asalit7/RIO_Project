import requests
import json
import pandas as pd
from pandas import json_normalize
import seaborn as sns
import uuid
import ast
from sqlalchemy import create_engine

# creating a list of the different pages of dungeons to use in the api
s3_dungeons = ['everbloom','ataldazar','black-rook-hold','doti-galakronds-fall','doti-murozonds-rise','darkheart-thicket','throne-of-the-tides','waycrest-manor']

# blank list to enter each api into based on their dungeon parameter
dungeons = []
# base api url
base_url = 'https://raider.io/api/v1/mythic-plus/runs'
# iterating through each dungeon in the s3_dungeons list to extrach the apis
for dungeon in s3_dungeons:
    # requesting api and inserting the current dungeon in the loop
    response = requests.get('https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon={}&page=0'.format(dungeon))
   
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
drop_col = ['run.keystone_team_id','run.dungeon.type','run.keystone_time_ms','run.logged_run_id','run.keystone_platoon_id','run.dungeon.id','run.dungeon.short_name','run.dungeon.expansion_id','run.status','run.videos','run.num_modifiers_active','run.faction','run.deleted_at','run.dungeon.num_bosses','run.dungeon.group_finder_activity_ids','run.platoon', 'run.dungeon.patch','run.dungeon.icon_url','run.dungeon.slug']

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
print(parties)
# scaling roster[1][0] -> [4][0]
# need to store each party into 1 cell? or within a row to match the run
# 
#{ 'role': 'dps', 'character.id': 150158626, 'character.persona_id': 41334465, 'character.name': 'Dragondik',  'character.class.name': 'Evoker', 'character.race.name': 'Dracthyr', 'character.race.faction': 'horde', 'character.spec.name': 'Augmentation', 'character.realm.name': 'Kazzak','character.region.short_name': 'EU', 
parties = {}
roster_num=0

for character in roster.iterrows():
    print(character)
    parties[roster_num] = character
    roster_num+=1





#df = full_df
#engine = create_engine("mysql+pymysql://root:Gulfstream2019!@localhost:3306/native_db", echo=False)
#df.to_sql('MDungeons', con=engine, index=False, if_exists='replace')


#character.name, character.class.name, character.race.name
#team = []


#r_df = pd.json_normalize(full_df['Roster'])
#r_df.head()
#r_df.shape
#r_df[4][2]
#for roster in range(0,r_df.shape[0]):
 #   char1 = r_df[0][roster]['character.name']
  #  char2 = r_df[1][roster]['character.name']
   # char3 = r_df[2][roster]['character.name']
    #char4 = r_df[3][roster]['character.name']
    #char5 = r_df[4][roster]['character.name']
    #curr_team = ', '.join([char1,char2,char3,char4,char5])
    #team.append((curr_team))


#print(team)
 #   characters.append(roster)


