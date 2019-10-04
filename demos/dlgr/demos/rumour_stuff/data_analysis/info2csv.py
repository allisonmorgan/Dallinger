import pandas as pd
import json
import os

# converts the info table to a csv where the column names are the dictionary keys in the parsed contents column

old_filename = 'data/pilot3x5x5_sept_30/info_uncleaned.csv' # the filename of the uncleaned info.csv file
new_filename = 'data/pilot3x5x5_sept_30/info_cleaned.csv' # the cleaned pilot data filename

os.chdir('/Users/mhardy/Documents/princeton_research/rumor_study/Dallinger/demos/dlgr/demos/rumour_stuff/data_analysis')

first_loop=True
data = pd.read_csv(old_filename)
for index,row in data.iterrows():
    if row['type']=='info' and row['origin_id']!=1 and row['failed']=='f' and row['contents'][0]=='{': # only want certain rows
        curr_json = json.loads(row['contents'])
        if first_loop: # get names of dictionary keys in contents and turn these into a list
            col_names = []
            for key in curr_json.keys():
                col_names.append(key)
            col_names.sort() # make column names in alphabetical order for simplicity
            cleaned_df = pd.DataFrame(columns=col_names) # make empty dataframe 
            first_loop=False
        curr_df_row = []
        for json_key in col_names: # loop through keys in the contents column and add the values to another list
            curr_df_row.append(curr_json[json_key])
        curr_df = pd.DataFrame([curr_df_row],columns=col_names)
        cleaned_df = cleaned_df.append(curr_df)

cleaned_df.to_csv(new_filename,index=False)