import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

ARK_db = 'Database/ARK_database.csv'
db_df = pd.read_csv(ARK_db)
db_df['date'] = pd.to_datetime(db_df['date'], format="%m/%d/%Y")
db_df['date'] = db_df['date'].dt.date
db_df['market value ($)'] = db_df['market value ($)'].str.replace('[$,]', '', regex=True).astype(float)
db_df['ticker'] = db_df['ticker'].str.replace(' UW', '', regex=True)
db_df['shares'] = db_df['shares'].str.replace(',', '', regex=True).astype(float)
print(db_df['date'][0])

fund_names = db_df['fund'].unique()

# Make a filtered dataset with the latest date
latest_date = db_df['date'].max()
latest_data = db_df[db_df['date'] == latest_date].copy()

# Make a pie chart for each fund
for funds in fund_names:
    ticker_names = latest_data[latest_data['fund'] == funds]['ticker'].unique()
    plt.pie(latest_data[latest_data['fund'] == funds]['market value ($)'], labels=ticker_names, autopct='%1.1f%%')
    #plt.show()

# Performance for top 25 holdings
hold_df = latest_data.groupby('ticker')['market value ($)'].sum().sort_values(ascending=False)
hold_tickers = hold_df[:25].index

print(hold_df[:25])

for ticks in hold_tickers:
    ticker = yf.Ticker(ticks)
    hist = ticker.history(period="1y")
    plt.plot(hist['Close'])
    plt.title(ticks)
    #plt.show()

# Display changes in holdings for each fund based on two date inputs
    # Caveat: Only works for dates that are included in the dataframe
date1 = '2025-03-07' #input("Enter the first date (YYYY-MM-DD): ")
date2 = '2025-03-21'#input("Enter the second date (YYYY-MM-DD): ")
date_format = "%Y-%m-%d"

# change inputs to date objects
try:
    date_object1 = datetime.strptime(date1, date_format).date()
    date_object2 = datetime.strptime(date2, date_format).date()
except ValueError:
    print("Incorrect date format, should be YYYY-MM-DD")

tar_fund = 'ARKW'

df_per1 = db_df[db_df['date'] == date_object1]
df_per2 = db_df[db_df['date'] == date_object2]

# Check to see if any holdings have changed
#hold_list1 = set(df_per1[df_per1['fund'] == tar_fund]['ticker'].unique())
#hold_list2 = set(df_per2[df_per2['fund'] == tar_fund]['ticker'].unique())

#new_tickers = hold_list2 - hold_list1
#print(new_tickers)

print(date_object1)

# Check the change in holdings for each fund
sliced_df = db_df[(db_df['date'] == date_object1) | (db_df['date'] == date_object2)]
grouped_df = sliced_df.groupby(['fund', 'ticker', 'date'])['shares'].sum().unstack().fillna(0)
grouped_df['change'] = grouped_df[date_object2] - grouped_df[date_object1]
print(grouped_df)

sliced_df = db_df[(db_df['date'] == date_object1) | (db_df['date'] == date_object2)]
grouped_df = sliced_df.groupby(['fund', 'ticker', 'date'])['market value ($)'].sum().unstack().fillna(0)
grouped_df['change'] = grouped_df[date_object2] - grouped_df[date_object1]
print(grouped_df)

