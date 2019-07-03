# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 14:21:33 2019

@author: cooneyg
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 14:26:01 2019

@author: cooneyg
"""

import pandas as pd
import eia

BAA = 'PJM'
BAA = ['PJM'] * 4
print(BAA)

data = {'BAA': BAA, 'primary': [3, 2, 1, 0], 'secondary': ['a', 'b', 'c', 'd']} 
pd.DataFrame.from_dict(data)



#What data structure should I use to store the information
#What do I ultimately want? dataframe? dictionary?
#It would seem like a dataframe would be helpful with columns of 1. reference BA, 2. Exchange BA, and 3. Relationship degree (e.g., primary, secondary, tertiary, etc)


# In[1]:
#required files:
#   1. 'BA_Codes_930.xlsx'
#   2. 'CA_Imports_Rows.csv'
#   3.'CA_Imports_Cols.csv'
#   4. 'CA_Imports_Gen.csv'

#Required non-standard packages:
#   1. eia - more info here: https://github.com/mra1385/EIA-python


import numpy as np
import os
import pandas as pd
import eia
from datetime import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt



#Read in BAA file which contains the names and abbreviations
df_BAA = pd.read_excel('data/BA_Codes_930.xlsx', sheetname = 'Table 1')
df_BAA.drop(df_BAA.index[:3], inplace=True)
df_BAA.rename(columns={'HOURLY AND DAILY BALANCING AUTHORITY': 'BAA_Acronym', 'Unnamed: 1': 'BAA_Name','Unnamed: 2': 'NRC_ID', 'Unnamed: 3': 'Region'}, inplace=True)
BAA = pd.np.array(df_BAA['BAA_Acronym'])


   
#%%
#Use the EIA python call to pull an example dataset from the EIA API
#Use this example dataset to figure out how to format dates
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
series_search = api.data_by_series(series= 'EBA.PJM-ALL.TI.H')
df = pd.DataFrame(series_search)
df.index

#Convert dataframe index of date strings to a list of date strings for processing 
date_list = df.index.tolist()

#Remove the last three characters from the date string 2015 0701T05Z 01; 
#Datetime won't process two instances of days of the month, so I have to remove the '01'
dates_trimmed = [x[:-3] for x in date_list]

#Use datetime.strptime to parse the sting into a datetime object
dates_formatted = [datetime.strptime(date, '%Y %m%dT%HZ') for date in dates_trimmed]

#Convert datetimes to timestamp - raw data comes in as Zulu time
dates_timestamp = [pd.Timestamp(date, tz = 'UTC') for date in dates_formatted]

#Convert UTC to US EST
dates_USEST = [date.tz_convert('US/Eastern') for date in dates_timestamp]

df_test = pd.DataFrame(index = dates_USEST)

#%%
#This portion of code reads in a file that contains the IDs for each of the BAAs in the U.S. 
#and Canada and creates a list of every combination of every single BAA ID (e.g. MISO-PJM). 
#The names are formatted as necessary to match the format for the EIA API call. 
BAA_combo = []
for i in range(1):
    for j in range (68):
        BAA_combo.append('EBA.'+BAA[i] + '-'+ BAA[j]+'.ID.H')

import eia
import pandas as pd
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
ba_trade_error_list = []
ba_match_list = []

#For a given BA, find what BAs it trades with based on a successful pull of the api.data_by_series query
#Add those names to a list
#Take names from the list and format them as individual BA names for next round of searching    
# eg . EBA.AEC-MISO.ID.H to MISO 

for k in range (68):
    try:
        series_search = api.data_by_series(series= str(BAA_combo[k]))
        ba_match_list.append(BAA_combo[k])
    
    except: 
        BAA_trade_error_list.append(BAA_combo[k])


#Take names from the list and format them as individual BA names for next round of searching    
# eg . EBA.AEC-MISO.ID.H to MISO 
ba_name_formatted_list = [x[(x.find('-'))+1:] for x in ba_match_list]
ba_name_formatted_list = [x[:(x.find('ID')-1)] for x in ba_name_formatted_list]


#Find matches for secondary interactions
ba_combo_2 = []
for i in range(1):
    for j in range (68):
        ba_combo_2.append('EBA.'+ ba_name_formatted_list[i] + '-'+ BAA[j]+'.ID.H')



ba_match_list_2 = []
for k in range (68):
    try:
        series_search = api.data_by_series(series= str(ba_combo_2[k]))
        ba_match_list_2.append(ba_combo_2[k])
    
    except: 
        print('no match')


#Take names from the list and format them as individual BA names for next round of searching    
# eg . EBA.AEC-MISO.ID.H to MISO 
ba_name_formatted_list_2 = [x[(x.find('-'))+1:] for x in ba_match_list_2]
ba_name_formatted_list_2 = [x[:(x.find('ID')-1)] for x in ba_name_formatted_list_2]

df_BAA.loc()

#create empty 68 x 68 dataframe with BA names as index and column names
df_network = pd.DataFrame(index = df_BAA['BAA_Acronym'], columns = df_BAA['BAA_Acronym'])
df_network = df_network.fillna(value = 0)

#
for i in range(len(ba_name_formatted_list)):
    df_network.loc['AEC', ba_name_formatted_list[i]] = 1
