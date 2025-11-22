import pandas as pd
import yaml
import os
import glob

def process_yaml(yaml_filepath):
        
        with open(yaml_filepath, 'r') as f:
            data = yaml.safe_load(f)

        return data

print("Module helps to load yaml data for a period of time and convert it into csv format")

src_dir=str(input('Give the source directory to read Stock data:'))
dest_dir=str(input('Give the target directory to write Product wise Stock data:'))

os.makedirs(dest_dir, exist_ok=True)


src_file_dirs = glob.glob(os.path.join(src_dir,'*'))
src_file_dirs.sort(reverse=True)
yml_data=pd.DataFrame()
file_count=1
for src_file_dir in src_file_dirs:
    if file_count <=12:
        print(src_file_dir)
    else:
        break
    file_count+=1
    yaml_files = glob.glob(os.path.join(src_file_dir, "*.yaml"))
    for f in yaml_files:
        print(f'Processing File:: {f}')
        if yml_data.empty:
            yml_data=pd.DataFrame(process_yaml(f))
        else:
            yml_data=pd.concat([yml_data,pd.DataFrame(process_yaml(f))],axis=0)

print('Final Shape after loading all files:',yml_data.shape)
print(yml_data.head(10))

# Data Transformation
yml_data['Date']=yml_data.apply(lambda x: str(str(x['date']).split("-")[2]).split(' ')[0] ,axis=1)
yml_data['Month']=yml_data.apply(lambda x: str(x['date']).split("-")[1],axis=1)
yml_data['Year']=yml_data.apply(lambda x: str(x['date']).split("-")[0],axis=1)

# Data cleansing
clean_data=yml_data.drop(columns=['date','month'])
print('ynl_data shape::',yml_data.shape)
print('Cleansed DF shape::',clean_data.shape)
print(clean_data.head(5))
print(clean_data['Ticker'].unique())

# Write the data after EDA
for i in clean_data['Ticker'].unique():
       ticker_wise_data = clean_data[clean_data['Ticker']==i]
       print(f"Total data for '{i}' : {ticker_wise_data.shape}")
       ticker_wise_data.to_csv(f'{dest_dir}{i}.csv',index=False)
