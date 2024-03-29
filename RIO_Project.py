import requests
import json
import pandas as pd
from pandas import json_normalize
import seaborn as sns
import uuid
import ast
from sqlalchemy import create_engine


# List of dungeon apis
#https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=everbloom&page=0
#  'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=ataldazar&page=0'
#  'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=black-rook-hold&page=0'
# 'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=doti-galakronds-fall&page=0'
# 'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=doti-murozonds-rise&page=0'
# 'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=darkheart-thicket&page=0'
# 'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=throne-of-the-tides&page=0'
# 'https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=waycrest-manor&page=0'


# Current goal:
# request apis -> throw in a nested dictionary = {dungeon : {run info}, etc}
# flatten json then convert into a database with each run showing the top 10 runs of each week
# clean, etc
# transfer database to a SQL database to essentially have a weekly automated entry of top 10 runs for each dungeon
# From there I can load that data into a visualization platform to create a dashboard/graphs
# showcase








response = requests.get('https://raider.io/api/v1/mythic-plus/runs?season=season-df-3&region=world&dungeon=all&page=0')
base_url = 'https://raider.io/api/v1/mythic-plus/runs'
params = {'season': 'season-df-3', 'region': 'world', 'dungeon': 'all'}


rank = []


for page in range(10):
    params['page'] = page
    response = requests.get(base_url, params=params)


    if response.status_code == 200:
        data = response.json()
        # Process the data as needed
        rank.append(data)
    else:
        print(f"Error fetching data from page {page + 1}. Status code: {response.status_code}")


# converting the nested list and dictionary of rankings from api to a dataframe
rank_df = pd.DataFrame(rank[0]['rankings'])


# normalizing a portion of the json format into a new dataframe
run_df = json_normalize(rank_df['run'])


# taking normalized or restructured code and concat to original dataframe to add as columns
rank_df = pd.concat([rank_df, run_df], axis=1)


# dropping original nested json column
rank_df = rank_df.drop('run', axis=1)


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
df.head()


# taking out the rankings column, has all the data i need
rankings = df['rankings']
rankings


# flattening the rankings more into a dataframe and viewing how it's formatted
nr = json_normalize(rankings)
nr.head()
json_normalize(nr.loc[0])


# creating blank dataframe to concat all the dungeon data together into a single dataframe
full_df = pd.DataFrame()


# iterating each dungeon dataframe into a single dataframe
for dungeon in range(0,7):
    current_dungeon = json_normalize(nr.loc[dungeon])
    full_df = pd.concat([full_df,current_dungeon])


# come back to 'run.roster' and 'run.weekly_modifiers'
# list of column names I want to drop
drop_col = ['run.roster','run.keystone_team_id','run.weekly_modifiers','run.platoon.name','run.keystone_time_ms','run.platoon.logo','run.platoon.id','run.platoon.short_name','run.platoon.slug','run.logged_run_id','run.keystone_platoon_id','run.dungeon.id','run.dungeon.short_name','run.dungeon.expansion_id','run.status','run.videos','run.num_modifiers_active','run.faction','run.deleted_at','run.dungeon.num_bosses','run.dungeon.group_finder_activity_ids','run.platoon', 'run.dungeon.patch','run.dungeon.icon_url','run.dungeon.slug']


# dropping columns in the list
full_df = full_df.drop(drop_col, axis=1)


full_df.info()


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
                                  'run.roster':'Roster'
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


full_df.tail()


df = full_df
engine = create_engine("mysql+pymysql://root:Gulfstream2019!@localhost:3306/native_db", echo=False)
df.to_sql('MDungeons', con=engine, index=False, if_exists='replace')


#json_normalize(full_df['Roster'])[0][0].keys()


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


