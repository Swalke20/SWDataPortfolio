import numpy as np
import pandas as pd
import json
import os

cricketer_filenames = []
for file in os.listdir('C:\Sophie Folder\Birkbeck\Project\Data\Cricketers_Wiki'):
    cricketer_filenames.append(os.path.join('C:\Sophie Folder\Birkbeck\Project\Data\Cricketers_Wiki',file))

cricketer_filenames[0:10]
len(cricketer_filenames)

dud_files = []

counter = 0
for file in cricketer_filenames:
    try: 
        with open(file) as f:
            d=json.load(f)
            d=pd.json_normalize(d, max_level=1)
        df = pd.concat([df,d])
        counter+=1
    
    except:
        dud_files.append(file)
        counter+=1
    print(counter)

len(dud_files)
print(df)
full_csv = df.to_csv('full_csv')

wiki_df = df[['name','role']]
wiki_df.rename(columns={'fullname': 'Name', 'role': 'Playing role'}, inplace=True)
print(wiki_df.shape)
wiki_df = wiki_df.dropna()
print(wiki_df.shape)
wiki_df = wiki_df.drop('Unnamed: 0', axis=1)
print(wiki_df)
wiki_df.to_csv('wiki_cricketers_csv')

dud_df = pd.DataFrame(dud_files)
dud_csv = dud_df.to_csv('dud_csv')
