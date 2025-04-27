import requests
import os
from datetime import date
import pandas as pd
import glob

# Download the CSV files from the given URLs
base_url = "https://assets.ark-funds.com/fund-documents/funds-etf-csv/"
csv_filenames = ['ARK_21SHARES_BITCOIN_ETF_ARKB_HOLDINGS.csv',
                 'ARK_AUTONOMOUS_TECH._&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv',
                 'ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv',
                 'ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv',
                 'ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv',
                 'ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL_HOLDINGS.csv',
                 'ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv',
                 'ARK_SPACE_EXPLORATION_&_INNOVATION_ETF_ARKX_HOLDINGS.csv',
                 'THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv'
                 ]


prefix = date.today().isoformat()
prefix += '_'

# Create a directory to store the downloaded files
download_dir = 'ARK_Files'
os.makedirs(download_dir, exist_ok=True)


for filename in csv_filenames:
    url = base_url + filename
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(download_dir, prefix + filename)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename}")
        print(file_path)
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

# Combine the downloaded CSV files into a single database
ARK_db = 'Database/ARK_database.csv'
csv_files = glob.glob('ARK_Files/*.csv')
db_df = pd.read_csv(ARK_db)

for file in csv_files:
    new_data = pd.read_csv(file)
    db_df = pd.concat([db_df, new_data], ignore_index=True)

db_df.dropna(inplace=True)
db_df = db_df.drop_duplicates(keep='first')
db_df.to_csv(ARK_db, index=False)
