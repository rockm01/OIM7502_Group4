import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

ARK_db = 'Database/ARK_database.csv'
db_df = pd.read_csv(ARK_db)
db_df['date'] = pd.to_datetime(db_df['date'], format='%m/%d/%Y') #store dates as datetime objects
db_df['market value ($)'] = db_df['market value ($)'].str.replace('[$,]', '', regex=True).astype(float)

fund_names = db_df['fund'].unique()

# Make a filtered dataset with the latest date
latest_date = db_df['date'].max()
latest_data = db_df[db_df['date'] == latest_date].copy()


# Make a pie chart for each fund
st.header('Current ARK Funds Holdings')
with st.container(border=True):
    sel_fund = st.selectbox('Select a fund', fund_names)

tab1, tab2 = st.tabs(['Pie Chart', 'Dataframe'])

fig1, ax1 = plt.subplots()
ax1.pie(latest_data[latest_data['fund'] == sel_fund]['market value ($)'], labels=latest_data[latest_data['fund'] == sel_fund]['ticker'], autopct='%1.1f%%')
tab1.pyplot(fig1)
tab2.dataframe(latest_data[latest_data['fund'] == sel_fund])
