import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import yfinance as yf
from datetime import datetime

ARK_db = 'Database/ARK_database.csv'
db_df = pd.read_csv(ARK_db)
db_df['date'] = pd.to_datetime(db_df['date'], format='%m/%d/%Y') #store dates as datetime objects
db_df['market value ($)'] = db_df['market value ($)'].str.replace('[$,]', '', regex=True).astype(float)
db_df['ticker'] = db_df['ticker'].str.replace(' UW', '', regex=True)
db_df['shares'] = db_df['shares'].str.replace(',', '', regex=True).astype(float)

#Preparations for use in Streamlit App
fund_names = db_df['fund'].unique() #Fund List for Selectbox

# Make a filtered dataset with the latest date
latest_date = db_df['date'].max()
latest_data = db_df[db_df['date'] == latest_date].copy()

date_opts = db_df['date'].unique() #list of dates

# Make a pie chart for each fund
st.header('ARK Funds')

st.markdown("Display Fund's Current Holdings")
with st.container(border=True):
    sel_fund = st.selectbox('Select a fund', fund_names)

tab1, tab2 = st.tabs(['Pie Chart', 'Dataframe'])

fig1, ax1 = plt.subplots()
ax1.pie(latest_data[latest_data['fund'] == sel_fund]['market value ($)'],
        autopct='%1.1f%%',
        pctdistance=1.3)
ax1.legend(labels=latest_data[latest_data['fund'] == sel_fund]['ticker'],
           loc='right',
           bbox_to_anchor=(1.0, 0., 0.5, 0.5))
tab1.pyplot(fig1)
tab2.dataframe(latest_data[latest_data['fund'] == sel_fund])

st.markdown('Funding Change Between Dates')

with st.container(border=True):
    fund2 = st.selectbox('Select Fund(s)', fund_names)

    left_column, right_column = st.columns(2)
    with left_column:
        start_date = st.selectbox("Start Date", date_opts)
        date_set = date_opts > start_date
        date_opts2 = date_opts[date_set]
    with right_column:
        end_date = st.selectbox("End Date", date_opts2)

    market_cap = st.toggle("Market Cap")
    if market_cap:
        filt = "market value ($)"
    else:
        filt = "shares"

sliced_df = db_df[(db_df['fund'] == fund2) & ((db_df['date'] == start_date) | (db_df['date'] == end_date))]
grouped_df = sliced_df.groupby(['fund', 'ticker', 'date'])[filt].sum().unstack().fillna(0)
grouped_df.reset_index(inplace=True)
grouped_df['change'] = grouped_df[end_date] - grouped_df[start_date]

tab1, tab2 = st.tabs(['Bar Chart', 'Dataframe'])
a_chart1 = alt.Chart(grouped_df).mark_bar(color='steelblue').encode(
    x=alt.X("ticker:O").axis(labelAngle=90),
    y=alt.Y("change:Q")
).properties(title="Bar Chart of Fund Holdings Change")
tab1.altair_chart(a_chart1)
tab2.dataframe(grouped_df, width=1600)