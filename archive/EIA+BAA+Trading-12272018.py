
# coding: utf-8

# In[1]:
#required files:
#'BA_Codes_930.xlsx'

import numpy as np
import os
import pandas as pd
import eia
from datetime import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt




df_BAA = pd.read_excel('BA_Codes_930.xlsx', sheetname = 'Table 1')
df_BAA.drop(df_BAA.index[:3], inplace=True)
df_BAA.rename(columns={'HOURLY AND DAILY BALANCING AUTHORITY': 'BAA_Acronym', 'Unnamed: 1': 'BAA_Name','Unnamed: 2': 'NRC_ID'}, inplace=True)
df_BAA.head()
BAA = pd.np.array(df_BAA['BAA_Acronym'])
print(BAA)


#Create series IDs for Total Interchange (TI), Net Generation (NG) and Demand (D)
#by taking BAA acronym and appending necessary text
BAA_names_tot_int = []
for i in range (len(BAA)):
    BAA_names_tot_int.append('EBA.'+ BAA[i]+'-ALL.TI.H')

BAA_names_net_gen = []
for i in range (len(BAA)):
    BAA_names_net_gen.append('EBA.'+ BAA[i]+'-ALL.NG.H')
    
BAA_names_dem = []
for i in range (len(BAA)):
    BAA_names_dem.append('EBA.'+ BAA[i]+'-ALL.D.H')
    


api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
### Retrieve Data By Series ID ###
series_search = api.data_by_series(series= 'EBA.PJM-ALL.TI.H')
df = pd.DataFrame(series_search)
df.head()
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
#This section is used to query the EIA API for all necessary data - it saves the data in pickle files.
#It is not necessary to run this if importing the data directly from the pickle files

#Query EIA for Total Interchange Data
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
### Retrieve Data By Series ID ###
df_tot_int = pd.DataFrame(index = df.index)
BAA_error_list = []
for k in range (68):
    try:
        series_search = api.data_by_series(series= str(BAA_names_tot_int[k]))
        df_tot_int[BAA_names_tot_int[k]] = pd.DataFrame(series_search)
    
    #except: Exception
    except: 
        BAA_error_list.append(BAA_names_tot_int[k])

df_tot_int.index = df_test.index
print(BAA_error_list)

#This code works to rename the columns to only the BAA name and strip the other text 
df_tot_int.columns = df_tot_int.rename(columns=lambda x: x[(x.find('.')+1):x.find('-')], inplace = True)

#Subset df_new so that it only contains data for 2016
df_tot_int_2016 = df_tot_int.loc['2016-01-01 01:00:00-04:00':'2016-12-31 23:00:00-04:00',]

#Add a new column that is the sum of all columns. Theoretically this should be zero if all of the imports/exports balance.
df_tot_int_2016['US_sum'] = df_tot_int_2016.sum(axis=1)
df_tot_int_2016.head()
df_tot_int_2016.to_pickle('2016_total_interchange.pkl')

df_tot_int_2016['US_sum'].resample('D')


#Query EIA for Net Generation Data
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
### Retrieve Data By Series ID ###
df_net_gen = pd.DataFrame(index = df.index)
BAA_net_gen_error_list = []
for k in range (68):
    try:
        series_search = api.data_by_series(series= str(BAA_names_net_gen[k]))
        df_net_gen[BAA_names_net_gen[k]] = pd.DataFrame(series_search)
    
    #except: Exception
    except: 
        BAA_error_list.append(BAA_names_net_gen[k])

df_net_gen.index = df_test.index
print(BAA_net_gen_error_list)


#This code works to rename the columns to only the BAA name and strip the other text 
df_net_gen.columns = df_net_gen.rename(columns=lambda x: x[(x.find('.')+1):x.find('-')], inplace = True)

#Subset df_new so that it only contains data for 2016
df_net_gen_2016 = df_net_gen.loc['2016-01-01 01:00:00-04:00':'2016-12-31 23:00:00-04:00',]

#Add a new column that is the sum of all columns. Theoretically this should be zero if all of the imports/exports balance.
df_net_gen_2016['US_sum'] = df_net_gen_2016.sum(axis=1)
df_net_gen_2016.head()
df_net_gen_2016.to_pickle('2016_net_gen.pkl')

#Sum rows for each BAA to get total net generation for 2016
df_net_gen_2016.loc['sum'] = df_net_gen_2016.sum()
df_net_gen_2016_tot = df_net_gen_2016.loc['sum']
df_net_gen_2016_tot.index

#Query EIA for Demand Data
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
### Retrieve Data By Series ID ###
df_dem = pd.DataFrame(index = df.index)
BAA_dem_error_list = []
for k in range (68):
    try:
        series_search = api.data_by_series(series= str(BAA_names_dem[k]))
        df_dem[BAA_names_dem[k]] = pd.DataFrame(series_search)
    
    #except: Exception
    except: 
        BAA_dem_error_list.append(BAA_names_dem[k])

df_dem.index = df_test.index
print(BAA_dem_error_list)

#This code works to rename the columns to only the BAA name and strip the other text 
df_dem.columns = df_dem.rename(columns=lambda x: x[(x.find('.')+1):x.find('-')], inplace = True)

#Subset df_new so that it only contains data for 2016
df_dem_2016 = df_dem.loc['2016-01-01 01:00:00-04:00':'2016-12-31 23:00:00-04:00',]

#Add a new column that is the sum of all columns. Theoretically this should be zero if all of the imports/exports balance.
df_dem_2016['US_sum'] = df_dem_2016.sum(axis=1)

df_dem_2016.to_pickle('2016_dem.pkl')

# #### This portion of code reads in a file that contains the IDs for each of the BAAs in the U.S. and Canada and creates a list of every combination of every single BAA ID (e.g. MISO-PJM). The names are formatted as necessary to match the format for the EIA API call. 
BAA_combo = []
for i in range(68):
    for j in range (68):
        BAA_combo.append('EBA.'+BAA[i] + '-'+ BAA[j]+'.ID.H')
BAA_combo_np = np.array(BAA_combo)
print(BAA_combo_np)
BAA_Names_DF = pd.DataFrame(BAA_combo_np, columns = ['Combo'])
BAA_Names_DF.head(10)


# ### Use the EIA API to collect all of the total net actual interchange data for each of the BAAs into a single dataframe. Check that the time index is consistent for all BAAs.
import eia
import pandas as pd
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
df_trade = pd.DataFrame(index = df.index)
BAA_trade_error_list = []
### Retrieve Data By Series ID ###
        
for k in range (4624):
    try:
        series_search = api.data_by_series(series= str(BAA_combo[k]))
        df_trade[BAA_combo[k]] = pd.DataFrame(series_search)
    
    #except: Exception
    except: 
        BAA_trade_error_list.append(BAA_combo[k])

df_trade.index = df_test.index
df_trade.index = df_test.index
df_trade.to_pickle('trade.pkl')

#Import trading data from EIA API
import eia
import pandas as pd
api_key = "d365fe67a9ec71960d69102951ae474f"
api = eia.API(api_key)
df_trade_all = pd.DataFrame(index = df.index)
BAA_trade_error_list = []
### Retrieve Data By Series ID ###    
for k in range (4624):
    try:
        series_search = api.data_by_series(series= str(BAA_combo[k]))
        df_trade_all[BAA_combo[k]] = pd.DataFrame(series_search)
    
    #except: Exception
    except: 
        df_trade_all[BAA_combo[k]] = 0

df_trade_all.index = df_test.index


df_trade_stack = df_trade.stack().to_frame().reset_index()
df_trade_stack.columns = ['Datetime', 'BAAs','Exchange']
df_trade_stack['BAAs'].astype('str')

df_trade_stack.set_index('Datetime',inplace = True)


#Subset df_new so that it only contains data for 2016
df_trade_stack_2016 = df_trade_stack.loc['2016-01-01 01:00:00-04:00':'2016-12-31 23:00:00-04:00']


df_trade_stack_2016['Exporting BAA'], df_trade_stack_2016['Importing BAA'] = df_trade_stack_2016['BAAs'].str.split('-', 1).str 
df_trade_stack_2016['Exporting BAA_1'] = df_trade_stack_2016['Exporting BAA'].str[4:] 
df_trade_stack_2016['Importing BAA_1'] = df_trade_stack_2016['Importing BAA'].str[0:-5] 
df_trade_stack_2016['Transacting BAAs'] = df_trade_stack_2016['Exporting BAA_1'] + '-' + df_trade_stack_2016['Importing BAA_1']
df_trade_stack_2016.head()   

df_trade_stack_2016.groupby(['Exporting BAA_1', 'Importing BAA_1'])['Exchange'].sum()
df_trade_stack_2016.groupby(['Importing BAA_1', 'Exporting BAA_1'])['Exchange'].sum()

df_trade_all_stack = df_trade_all.stack().to_frame().reset_index()
df_trade_all_stack.columns = ['Datetime', 'BAAs','Exchange']
df_trade_all_stack['BAAs'].astype('str')

df_trade_all_stack.set_index('Datetime',inplace = True)

df_trade_all_stack.head()
#Subset df_new so that it only contains data for 2016
df_trade_all_stack_2016 = df_trade_all_stack.loc['2016-01-01 01:00:00-04:00':'2016-12-31 23:00:00-04:00']

df_trade_all_stack_2016.to_pickle('trade_all_2016.pkl')

df_trade_all_stack_2016['Exporting BAA'], df_trade_all_stack_2016['Importing BAA'] = df_trade_all_stack_2016['BAAs'].str.split('-', 1).str 
df_trade_all_stack_2016['Exporting BAA_1'] = df_trade_all_stack_2016['Exporting BAA'].str[4:] 
df_trade_all_stack_2016['Importing BAA_1'] = df_trade_all_stack_2016['Importing BAA'].str[0:-5] 
df_trade_all_stack_2016['Transacting BAAs'] = df_trade_all_stack_2016['Exporting BAA_1'] + '-' + df_trade_all_stack_2016['Importing BAA_1']



# In[8]:
#Read pickle files

df_trade_all_stack_2016 = pd.read_pickle('trade_all_2016.pkl')
df_trade = pd.read_pickle('trade.pkl')
df_dem_2016 = pd.read_pickle('2016_dem.pkl')
df_net_gen_2016 = pd.read_pickle('2016_net_gen.pkl')
df_tot_int_2016 = pd.read_pickle('2016_total_interchange.pkl')

#Net gen dataset has some erroneous values for two BAAs - PACW and SEC; clean manually and reimport; need to think about automatic quality checking instead
#df_net_gen_2016_clean = pd.read_csv('df_net_gen_2016_clean.csv', index_col = 0)

#df_net_gen_2016 = df_net_gen_2016_clean

#Group and resample trading data so that it is on an annual basis
df_trade_all_stack_2016_resamp = df_trade_all_stack_2016.groupby('BAAs').resample('A').sum()
df_trade_all_stack_2016_resamp_stack = df_trade_all_stack_2016_resamp.stack().to_frame().reset_index()
df_trade_all_stack_2016_resamp_stack = df_trade_all_stack_2016_resamp_stack.set_index('Datetime')
del df_trade_all_stack_2016_resamp_stack['level_2']
df_trade_all_stack_2016_resamp_stack.columns = ['BAAs','Exchange']


#Split BAA string into exporting and importing BAA columns
df_trade_all_stack_2016_resamp_stack['BAA1'], df_trade_all_stack_2016_resamp_stack['BAA2'] = df_trade_all_stack_2016_resamp_stack['BAAs'].str.split('-', 1).str 
df_trade_all_stack_2016_resamp_stack['BAA1'] = df_trade_all_stack_2016_resamp_stack['BAA1'].str[4:] 
df_trade_all_stack_2016_resamp_stack['BAA2'] = df_trade_all_stack_2016_resamp_stack['BAA2'].str[0:-5] 
df_trade_all_stack_2016_resamp_stack['Transacting BAAs'] = df_trade_all_stack_2016_resamp_stack['BAA1'] + '-' + df_trade_all_stack_2016_resamp_stack['BAA2']


#Create two perspectives - import and export to use for comparison in selection of the final exchange value between the BAAs
df_trade_sum_1_2 = df_trade_all_stack_2016_resamp_stack.groupby(['BAA1', 'BAA2','Transacting BAAs'], as_index=False)[['Exchange']].sum()
df_trade_sum_2_1 = df_trade_all_stack_2016_resamp_stack.groupby(['BAA2', 'BAA1', 'Transacting BAAs'], as_index=False)[['Exchange']].sum()
df_trade_sum_1_2.columns = ['BAA1_1_2', 'BAA2_1_2','Transacting BAAs_1_2', 'Exchange_1_2']
df_trade_sum_2_1.columns = ['BAA2_2_1', 'BAA1_2_1','Transacting BAAs_2_1', 'Exchange_2_1']

#Combine two grouped tables for comparison for exchange values
df_concat_trade = pd.concat([df_trade_sum_1_2,df_trade_sum_2_1], axis = 1)
df_concat_trade['Exchange_1_2_abs'] = df_concat_trade['Exchange_1_2'].abs()
df_concat_trade['Exchange_2_1_abs'] = df_concat_trade['Exchange_2_1'].abs()

#Create new column to check if BAAs designate as either both exporters or both importers
#or if one of the entities in the transaction reports a zero value
df_concat_trade['Status_Check'] = np.where(((df_concat_trade['Exchange_1_2'] > 0) & (df_concat_trade['Exchange_2_1'] > 0)) \
               |((df_concat_trade['Exchange_1_2'] < 0) & (df_concat_trade['Exchange_2_1'] < 0)) \
               | ((df_concat_trade['Exchange_1_2'] == 0) | (df_concat_trade['Exchange_2_1'] == 0)), 'drop', 'keep') 

#Calculate the difference in exchange values
df_concat_trade['Delta'] = df_concat_trade['Exchange_1_2_abs'] - df_concat_trade['Exchange_2_1_abs']

#Calculate percent diff of exchange_abs values - this can be down two ways:
#relative to 1_2 exchange or relative to 2_1 exchange - perform the calc both ways
#and take the average
df_concat_trade['Percent_Diff_Avg']= ((abs((df_concat_trade['Exchange_1_2_abs']/df_concat_trade['Exchange_2_1_abs'])-1)) \
    + (abs((df_concat_trade['Exchange_2_1_abs']/df_concat_trade['Exchange_1_2_abs'])-1)))/2

#Mean exchange value
df_concat_trade['Exchange_mean'] = df_concat_trade[['Exchange_1_2_abs', 'Exchange_2_1_abs']].mean(axis=1)

#Percent diff equations creats NaN where both values are 0, fill with 0
df_concat_trade['Percent_Diff_Avg'].fillna(0, inplace = True)

#Final exchange value based on logic; if percent diff is less than 20%, take mean, 
#if not use the value as reported by the exporting BAA. First figure out which BAA is the exporter 
#by checking the value of the Exchance_1_2
#If that value is positive, it indicates that BAA1 is exported to BAA2; if negative, use the 
#value from Exchange_2_1
df_concat_trade['Final_Exchange'] = np.where((df_concat_trade['Percent_Diff_Avg'].abs() < 0.2), 
               df_concat_trade['Exchange_mean'],np.where((df_concat_trade['Exchange_1_2'] > 0), 
                              df_concat_trade['Exchange_1_2'],df_concat_trade['Exchange_2_1']))


#Assign final designation of BAA as exporter or importer based on logical assignment
df_concat_trade['Export_BAA'] = np.where((df_concat_trade['Exchange_1_2'] > 0), df_concat_trade['BAA1_1_2'],
               np.where((df_concat_trade['Exchange_1_2'] < 0), df_concat_trade['BAA2_1_2'],''))

df_concat_trade['Import_BAA'] = np.where((df_concat_trade['Exchange_1_2'] < 0), df_concat_trade['BAA1_1_2'],
               np.where((df_concat_trade['Exchange_1_2'] > 0), df_concat_trade['BAA2_1_2'],''))

df_concat_trade = df_concat_trade[df_concat_trade['Status_Check'] == 'keep']

df_concat_trade.to_csv('tradeout.csv')



#Create the final trading matrix; first grab the necessary columns, rename the columns and then pivot
df_concat_trade_subset = df_concat_trade[['Export_BAA', 'Import_BAA', 'Final_Exchange']]

df_concat_trade_subset.columns = ['Exporting_BAA', 'Importing_BAA', 'Amount']



#df_concat_trade_subset = df_concat_trade_subset.drop_duplicates()

df_trade_pivot = df_concat_trade_subset.pivot_table(index = 'Exporting_BAA', columns = 'Importing_BAA', values = 'Amount').fillna(0)


#Find missing BAAs - need to add them in so that we have a square matrix
cols = list(df_trade_pivot.columns.values)
rows = list(df_trade_pivot.index.values)

cols_set = set(cols)
rows_set = set(rows)
BAA_ref_set = set(BAA) 

col_diff = list(BAA_ref_set - cols_set)
col_diff.sort(key = str.upper)

row_diff = list(BAA_ref_set - rows_set)
row_diff.sort(key=str.upper)

#Add in missing columns, then sort in alphabetical order
for i in col_diff:
    df_trade_pivot[i] = 0

df_trade_pivot = df_trade_pivot.sort_index(axis=1)

#Add in missing rows, then sort in alphabetical order
for i in row_diff:
    df_trade_pivot.loc[i,:] = 0

df_trade_pivot = df_trade_pivot.sort_index(axis=0)

#Add Canadian Imports
#This matrix includes only CA_imports to the designated BAA, need to add to df_trade_pivot 
df_CA_Imports_Rows = pd.read_csv('CA_Imports_Rows.csv', index_col = 0)
df_CA_Imports_Cols = pd.read_csv('CA_Imports_Cols.csv', index_col = 0)

df_concat_trade_CA = pd.concat([df_trade_pivot, df_CA_Imports_Rows])
df_concat_trade_CA = pd.concat([df_concat_trade_CA, df_CA_Imports_Cols], axis = 1)
df_concat_trade_CA.fillna(0, inplace = True)
df_trade_pivot = df_concat_trade_CA
df_trade_pivot = df_trade_pivot.sort_index(axis=0)
df_trade_pivot = df_trade_pivot.sort_index(axis=1)


#Define the values for p (electricity generation) for the trading math
#Add in missing BAAs to the net generation dataframe, assume zero values (no data available)
df_net_gen_2016 = df_net_gen_2016.drop('US_sum', axis = 1)
df_net_gen_2016['GRIS'], df_net_gen_2016['WAUE'] = [0,0]

#Resort columns so the headers are in alpha order
df_net_gen_2016.sort_index(axis=1, inplace=True)

#Sum values in each column
df_net_gen_2016_sum = df_net_gen_2016.sum(axis = 0).to_frame()

#Add Canadian import data to the net generation dataset
df_CA_Imports_Gen = pd.read_csv('CA_Imports_Gen.csv', index_col = 0)

df_net_gen_2016_sum = pd.concat([df_net_gen_2016_sum,df_CA_Imports_Gen]).sum(axis=1)

df_net_gen_2016_sum = df_net_gen_2016_sum.to_frame()

df_net_gen_2016_sum = df_net_gen_2016_sum.sort_index(axis=0)
#%%
#Create total inflow vector x and then convert to a diagonal matrix x-hat

x = []
for i in range (len(df_net_gen_2016_sum)):
    x.append(df_net_gen_2016_sum.iloc[i] + df_trade_pivot.sum(axis = 0).iloc[i])

x_np = np.array(x)

#If values are zero, x_hat matrix will be singular, set BAAs with 0 to small value (1)
df_x = pd.DataFrame(data = x_np, index = df_trade_pivot.index)
df_x = df_x.rename(columns = {0:'inflow'})
df_x.loc[df_x['inflow'] == 0] = 1

x_np = df_x.values
 
x_hat = np.diagflat(x_np)

#Create consumption vector c and then convert to a digaonal matrix c-hat

c = []

for i in range(len(df_net_gen_2016_sum)):
    c.append(x[i] - df_trade_pivot.sum(axis = 1).iloc[i])
    
c_np = np.array(c)
c_hat = np.diagflat(c_np)

#Convert df_trade_pivot to matrix
T = df_trade_pivot.values

#Create matrix to split T into distinct interconnections - i.e., prevent trading between eastern and western interconnects
#Connections between the western and eastern interconnects are through SWPP and WAUE
interconnect = df_trade_pivot.copy()
interconnect[:] = 1
interconnect.loc['SWPP',['EPE', 'PNM', 'PSCO', 'WACM']] = 0
interconnect.loc['WAUE',['WAUW', 'WACM']] = 0
interconnect_mat = interconnect.values
T_split = np.multiply(T, interconnect_mat)

#Export x and c vectors to csv to check
np.savetxt("output/x_vector.csv", x_np, delimiter=",")
np.savetxt("output/c_vector.csv", c_np, delimiter=",")
np.savetxt("output/c_hat.csv", c_hat, delimiter=",")
np.savetxt("output/x_hat_matrix.csv", x_hat, delimiter=",")
df_net_gen_2016_sum.to_csv('output/p_vector.csv')
#Export trade pivot to csv to check
df_trade_pivot.to_csv('output/df_trade_pivot.csv')
np.savetxt("output/T_split.csv", T_split, delimiter=",")
#Matrix trading math (see Qu et al. 2018 ES&T paper)
x_hat_inv = np.linalg.inv(x_hat)

np.savetxt("output/x_hat_inv_matrix.csv", x_hat_inv, delimiter=",")

B = np.matmul(x_hat_inv,T_split)

I = np.identity(len(df_net_gen_2016_sum))
np.savetxt("output/I.csv", I, delimiter=",")

diff_I_B = I - B

G = np.linalg.inv(diff_I_B)

c_hat_x_hat_inv = np.matmul(c_hat, x_hat_inv)
np.savetxt("output/c_hat_x_hat_inv_matrix.csv", c_hat_x_hat_inv, delimiter=",")

G_c = np.matmul(G, c_hat)
H = np.matmul(G,c_hat, x_hat_inv)

df_G = pd.DataFrame(G)
df_G.to_csv('output/G_matrix.csv')
df_B = pd.DataFrame(B)
df_B.to_csv('output/B_matrix.csv')
df = pd.DataFrame(H)
df.to_csv('output/H_matrix.csv')



#%%
#Convert H to pandas dataframe, populate index and columns
df_final_trade_out = pd.DataFrame(data = H)
df_final_trade_out.columns = df_net_gen_2016_sum.index
df_final_trade_out.index = df_net_gen_2016_sum.index
df_final_trade_out.reset_index(inplace = True)
df_final_trade_out.rename(columns = {'index':'Source BAA'}, inplace= True)


#Melt dataframe
df_final_trade_out_melt = pd.melt(df_final_trade_out, id_vars='Source BAA', value_vars= df_final_trade_out.columns.values.tolist()[1:], var_name = 'Dest BAA', value_name = 'MWh_consumed')


#Import generation data from EIA860 and 923; merge with final trade data, calculate 'MWh by type' of generation
df_860_923 = pd.read_csv('EIA860_923 2016 Generation Data.csv')
df_merged = df_860_923.merge(df_final_trade_out_melt, left_on = 'BAA', right_on = 'Source BAA')
df_merged.rename(columns = {'BAA_x':'BAA'}, inplace=True)
df_merged['MWh_by_type'] = df_merged['MWh_consumed']*df_merged['Fuel Type Gen %']
df_merged.drop(['Unnamed: 0','BAA', 'Fuel Type Gen MWh'], axis =1, inplace= True)


#Groupby sum of MWh by type by BAA
df_merged_grouped_BAA_tot_cons = df_merged.groupby(['Dest BAA'])['MWh_by_type'].sum().reset_index()
df_merged_grouped_BAA_tot_cons.columns = ['Dest BAA','BAA_Tot_Cons']

#Calculate BAA fuel % by tehcnology
df_merged = df_merged.merge(df_merged_grouped_BAA_tot_cons, left_on = 'Dest BAA', right_on = 'Dest BAA')
df_merged['BAA_Fuel_%'] = df_merged['MWh_by_type']/df_merged['BAA_Tot_Cons']

#Groupby BAA and fuel type
df_final_BAA_cons_by_fuel = df_merged.groupby(['Dest BAA', 'Fuel Type'])['BAA_Fuel_%'].sum().reset_index()
df_final_BAA_cons_by_fuel.to_csv('Final_BAA_Cons_Mix.csv')

#Pivot data to desired format (BAA by technology share in consumption mix)
df_pivot_cons_mix = df_final_BAA_cons_by_fuel.pivot(index = 'Dest BAA', columns= 'Fuel Type', values= 'BAA_Fuel_%')
df_pivot_cons_mix = df_pivot_cons_mix.fillna(0)

#%%
#Create grid gen and consumption heat maps
plt.figure(figsize=(20, 4))
grid_gen_plot = sns.heatmap(df_pivot_cons_mix.transpose(), cmap='Greens')
fig = grid_gen_plot.get_figure()
fig.savefig('grid_cons_plot.png')
plt.show()

#Subset to grab only 10 BAAs
df_pivot_cons_mix_sub = df_pivot_cons_mix.loc[['PJM','MISO', 'ERCO', 'SWPP', 'SOCO', 'CISO', 'NYIS', 'TVA', 'ISNE']]
df_pivot_cons_mix_sub

sns.set(font_scale=2) 
plt.figure(figsize=(15, 10))
grid_gen_plot_sub = sns.heatmap(df_pivot_cons_mix_sub.transpose(), cmap='Greens',vmin = 0, vmax = 0.5)
grid_gen_plot_sub.set(xlabel='BA')
fig2 = grid_gen_plot_sub.get_figure()
fig2.savefig('grid_cons_plot_sub.png')
plt.show()


#Calculate environmental impacts by BAA for consumption mix
df_cons_BAA = df_merged.copy()
df_cons_BAA.drop(['Fuel Type','Total BAA Gen MWh', 'Fuel Type Gen %','MWh_consumed', 'MWh_by_type', 'BAA_Tot_Cons'],axis = 1, inplace =True)
df_cons_BAA = df_cons_BAA.groupby(['Source BAA', 'Dest BAA'])['BAA_Fuel_%'].sum().reset_index()

#Import output from impact tech compilation
df_US_CA_BAA_gen = pd.read_csv('df_US_CA_BAA_gen.csv')

#Merge dataframes and calculate wtd impact, groupby destinaiton BAA
df_cons_BAA_merge = df_cons_BAA.merge(df_US_CA_BAA_gen, left_on = 'Source BAA', right_on = 'Balancing Authority Code')
df_cons_BAA_merge['BAA_Cons_Impact'] = df_cons_BAA_merge['BAA_Fuel_%'] * df_cons_BAA_merge['Wtd Fuel Impact']
df_cons_BAA_merge = df_cons_BAA_merge.groupby(['Dest BAA','Impact'])['BAA_Cons_Impact'].sum().reset_index()
df_cons_BAA_pivot = df_cons_BAA_merge.pivot(index = 'Dest BAA', columns= 'Impact', values= 'BAA_Cons_Impact')
df_cons_BAA_pivot.to_csv('df_cons_BAA_pivot.csv')

#Select top  BAs based on consumption
df_cons_BAA_pivot_sub = df_cons_BAA_pivot.loc[['PJM', 'MISO', 'ERCO', 'SWPP', 'SOCO', 'CISO', 'NYIS', 'TVA', 'ISNE']]
df_cons_BAA_pivot_sub.to_csv('df_cons_BAA_pivot_sub.csv') 
df_cons_BAA_pivot_sub_norm = pd.read_csv('df_cons_BAA_pivot_sub_norm.csv', index_col = 0)

#Create normalized heat map for env impacts - Consumption
sns.set(font_scale=2) 
plt.figure(figsize=(10, 6))
gen_mix_impact_plot = sns.heatmap(df_cons_BAA_pivot_sub_norm.transpose(), cmap='Blues',vmin = 0, vmax = 1.0)
fig3 = grid_gen_plot_sub.get_figure()
fig3.savefig('grid_cons_impact_plot_sub.png')
plt.show()


#Calculate environmental impacts by BAA for generation mix; this is just the data that we have coming out of the tech compilation
df_US_CA_BAA_gen_pivot = pd.pivot_table(df_US_CA_BAA_gen,index = 'Balancing Authority Code', columns = 'Impact', values = 'Wtd Fuel Impact')
df_US_CA_BAA_gen_pivot.to_csv('df_US_CA_BAA_gen_pivot.csv')

#Select top BAs based on consumption
df_US_CA_BAA_gen_pivot_sub = df_US_CA_BAA_gen_pivot.loc[['PJM', 'MISO', 'ERCO', 'SWPP', 'SOCO', 'CISO', 'NYIS', 'TVA', 'TVA', 'ISNE']]
df_US_CA_BAA_gen_pivot_sub.to_csv('df_US_CA_BAA_gen_pivot_sub.csv')
df_US_CA_BAA_gen_pivot_sub_norm =  pd.read_csv('df_US_CA_BAA_gen_pivot_sub_norm.csv', index_col = 0)

#Create normalized heat map for env impacts - Generation
sns.set(font_scale=2) 
plt.figure(figsize=(10, 6))
gen_mix_impact_plot = sns.heatmap(df_US_CA_BAA_gen_pivot_sub_norm.transpose(), cmap='Blues',vmin = 0, vmax = 1.0)
fig4 = grid_gen_plot_sub.get_figure()
fig4.savefig('grid_gen_impact_plot_sub.png')
plt.show()




BAA_cons_rank = df_merged.groupby('Dest BAA')['BAA_Tot_Cons'].mean().reset_index()


df_cons_BAA_pivot_sub_norm.columns = ['AP', 'EP', 'GWP', 'PM', 'ODP', 'Smog']

sns.set(font_scale=2) 
plt.figure(figsize=(16, 8))
gen_mix_impact_plot = sns.heatmap(df_cons_BAA_pivot_sub_norm.transpose(), cmap="YlGnBu",vmin = 0, vmax = 1.0)
gen_mix_impact_plot.set(xlabel='BA')
gen_mix_impact_plot.set_yticklabels(gen_mix_impact_plot.get_yticklabels(), rotation = 0)
gen_mix_impact_plot.savefig('grid_cons_impact_plot_sub.png')
plt.show()


df_gen_cons_comp_sub = pd.read_csv('df_gen_cons_comp_sub.csv', index_col = 0)
sns.set(font_scale=2) 
plt.figure(figsize=(16, 8))
gen_mix_impact_plot = sns.heatmap(df_gen_cons_comp_sub.transpose(),cmap = "RdBu_r", vmin = -1, vmax = 1)
gen_mix_impact_plot.set_yticklabels(gen_mix_impact_plot.get_yticklabels(), rotation = 0)
fig6 = gen_mix_impact_plot.get_figure()
fig6.savefig('grid_gen_cons_comp_sub.png')
plt.show()



# In[27]:

#Look at demand, net gen, and interchange at a high level to compare BAAs
#Format demand data

df_dem_2016.head()
#Drop US_sum column

df_dem_2016.drop(['US_sum'], axis=1, inplace = True)

#Resort columns so the headers are in alpha order

df_dem_2016.sort_index(axis=1, inplace=True)


#Sum values in each column
df_dem_2016_sum = df_dem_2016.sum(axis = 0).reset_index()

df_dem_2016_sum.columns = ['BAA','EIA_Demand']


#Format total interchange data

#Drop US_sum column

df_tot_int_2016.drop(['US_sum'], axis=1, inplace = True)

#Resort columns so the headers are in alpha order

df_tot_int_2016.sort_index(axis=1, inplace=True)


#Sum values in each column
df_tot_int_2016_sum = df_tot_int_2016.sum(axis = 0).reset_index()

df_tot_int_2016_sum.columns = ['BAA','EIA_Interchange']

df_tot_int_2016_sum.head()

#Join 2016 tables for net gen, demand, total interchange

df_net_gen_2016_sum_2 = df_net_gen_2016.sum(axis = 0).reset_index()
df_net_gen_2016_sum_2.columns = ['BAA','EIA_Net_Gen']

df_2016_summary = pd.merge(pd.merge(df_net_gen_2016_sum_2,df_tot_int_2016_sum,on='BAA'),df_dem_2016_sum,on='BAA') 

df_2016_summary['Calc_Demand'] = df_2016_summary['EIA_Net_Gen'] - df_2016_summary['EIA_Interchange']
df_2016_summary['Demand_Percent_Diff'] = df_2016_summary['Calc_Demand']/df_2016_summary['EIA_Demand']-1
df_2016_summary['Net Gen - Demand'] = df_2016_summary['EIA_Net_Gen'] - df_2016_summary['EIA_Demand']

df_2016_summary.to_csv('df_2016_EIA_summary.csv')


