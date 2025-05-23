import pandas as pd
import glob

ARK_db = 'Database/ARK_database.csv'

csv_files = glob.glob('ARK_files/*.csv')

print(csv_files)

db_df = pd.read_csv(ARK_db)

for file in csv_files:
    new_data = pd.read_csv(file)
    db_df = pd.concat([db_df, new_data], ignore_index=True)


db_df.dropna(inplace=True)
db_df = db_df.drop_duplicates(keep='first')
print(db_df)
db_df.to_csv(ARK_db, index=False)
