import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import yfinance as yf
from datetime import datetime
from stock_class import Stock

ARK_db = 'Database/ARK_database.csv'
db_df = pd.read_csv(ARK_db)
db_df['date'] = pd.to_datetime(db_df['date'], format='%m/%d/%Y') #store dates as datetime objects
db_df['market value ($)'] = db_df['market value ($)'].str.replace('[$,]', '', regex=True).astype(float)
db_df['ticker'] = db_df['ticker'].str.replace(' UW', '', regex=True)
db_df['shares'] = db_df['shares'].str.replace(',', '', regex=True).astype(float)

#Setup the sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Fund Information", "Investment Strategy"])
# Preparations for use in Streamlit App
fund_names = db_df['fund'].unique()  # Fund List for Selectbox
# Grab dates that are included in dataset:
latest_date = db_df['date'].max()
latest_data = db_df[db_df['date'] == latest_date].copy()
date_opts = db_df['date'].unique()  # list of dates

if page == "Fund Information":

    ##========== Display a filtered dataset with the latest date ==========##
    #Start Section
    st.title('ARK Funds Information')

    st.markdown("## Display Fund's Current Holdings")
    with st.container(border=True):
        sel_fund = st.selectbox('Select a fund', fund_names)

    #Create Tabs to flip between pie chart and dataframe
    tab1, tab2 = st.tabs(['Pie Chart', 'Dataframe'])

    #Create Pie Charts
    fig1, ax1 = plt.subplots()
    ax1.pie(latest_data[latest_data['fund'] == sel_fund]['market value ($)'],
            autopct='%1.1f%%',
            pctdistance=1.3)
    ax1.legend(labels=latest_data[latest_data['fund'] == sel_fund]['ticker'],
               loc='right',
               bbox_to_anchor=(1.0, 0., 0.5, 0.5))
    tab1.pyplot(fig1)
    #Create Dataframe
    tab2.dataframe(
        latest_data[latest_data['fund'] == sel_fund][
            ['fund', 'company', 'ticker', 'shares', 'market value ($)', 'weight (%)'
             ]
        ],
        width=800, hide_index=True
    )

    st.divider()

    ##========== Display Fund Holding Changes between dates ==========##
    st.markdown('## Funding Change Between Dates')

    # Start Section
    with st.container(border=True):
        fund2 = st.selectbox('Select Fund(s)', fund_names)

        # Have start and end date inputs set side by side
        left_column, right_column = st.columns(2)
        with left_column:
            start_date = st.selectbox("Start Date", date_opts)
            date_set = date_opts > start_date
            date_opts2 = date_opts[date_set]
        with right_column:
            end_date = st.selectbox("End Date", date_opts2)

        # Allow toggling between changes in shares vs market cap
        market_cap = st.toggle("Market Cap")
        if market_cap:
            filt = "market value ($)"
        else:
            filt = "shares"

    # Filter and group the data
    sliced_df = db_df[(db_df['fund'] == fund2) & ((db_df['date'] == start_date) | (db_df['date'] == end_date))]
    grouped_df = sliced_df.groupby(['fund', 'ticker', 'date'])[filt].sum().unstack().fillna(0)
    grouped_df.reset_index(inplace=True)
    grouped_df['change'] = grouped_df[end_date] - grouped_df[start_date]

    # Create Tabs to flip between bar chart and dataframe
    tab1, tab2 = st.tabs(['Bar Chart', 'Dataframe'])
    a_chart1 = alt.Chart(grouped_df).mark_bar(color='steelblue').encode(
        x=alt.X("ticker:O").axis(labelAngle=90),
        y=alt.Y("change:Q")
    ).properties(title="Bar Chart of Fund Holdings Change")
    tab1.altair_chart(a_chart1)
    tab2.dataframe(grouped_df, width=1600)

if page == "Investment Strategy":
    st.header('Investment Strategy')
    st.markdown("## Choose the fund you're using to determine investment strategy:")

    with st.container(border=True):
        sel_fund = st.selectbox('Select a fund', fund_names)

    stocks = db_df[db_df['fund'] == sel_fund]['ticker'].unique()
    stocks = stocks.tolist()
    stocks = [(lambda x: x.replace(" UQ", ""))(item) for item in stocks]
    stocks = stocks[:10]
    ## ========== Display Stock Returns ==========##
    # stock_class file created to house the Stocks class.
    # Call the file
    def main():
        mystocks = Stock(stocks)
        new_df = mystocks.calc_returns()
        return mystocks, new_df

    if __name__ == "__main__":
        mystocks, new_df = main()

    tab1, tab2, tab3 = st.tabs(['Line Graph','Returns', 'Dataframe'])
    fig, ax = plt.subplots()
    graph_df = (mystocks.data.unstack()).reset_index()
    graph_df = graph_df[graph_df['Price'] == 'Close']
    graph_df = graph_df.rename(columns={0: "Value"})
    #tab1.write(graph_df)
    tab1.line_chart(graph_df, x='Date', y='Value', color='Ticker')
    tab2.write(new_df)
    tab3.write(graph_df)

    # Create a line graph
    fig, ax = plt.subplots()


