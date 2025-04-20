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
    st.markdown("#### Choose the fund you're using to determine investment strategy:")

    with st.container(border=True):
        sel_fund = st.selectbox('Select a fund', fund_names)

        left, right = st.columns(2)
        with left:
            num = st.text_input('Number of Periods')
        with right:
            prd_type = st.selectbox('Period Type', ['d', 'mo', 'y'], index=1)

        prd = num + prd_type
        st.write(f"Selected Period: {prd}")


    # Filter the database for selected fund and get the top 10 holdings
    stocks = db_df[db_df['fund'] == sel_fund]['ticker'].unique()
    stocks = stocks.tolist()
    stocks = [(lambda x: x.replace(" UQ", ""))(item) for item in stocks]
    stocks = stocks[:10]


    ## ========== Display Stock Returns ==========##
    # stock_class file created to house the Stocks class.
    # Call the file
    def main():
        mystocks = Stock(stocks, period=prd)
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
    tab1.line_chart(graph_df, x='Date', y='Value',
                    color='Ticker',
                    x_label='Date', y_label='Ticker Price ($)'
                    )
    tab2.write(new_df, width=1200, hide_index=True)
    tab3.write(graph_df, width=1200, hide_index=True)

    # Create a line graph
    fig, ax = plt.subplots()

st.divider()

st.markdown('#### Our Investment Recommendation')
st.write("Based on the analysis of the selected fund's top holdings, we recommend focusing on the following strategies:")
tot_ret = new_df['Returns'].sum()


with st.container(border=True):
    st.markdown("#### Investment Strategy for Aggregated Fund")



    if tot_ret > 0:
        st.write(''':chart_with_upwards_trend:''', f"{sel_fund} Cumulative Return: :green[${tot_ret:.2f}]")
        st.write(f":green[*Overall returns for {sel_fund} are positive. If you are using entire fund as an investment reference"
                 f", we recommend going long in the fund*]")
    else:
        st.write(''':chart_with_downwards_trend:''', f"{sel_fund} Cumulative Return: :red[${tot_ret:.2f}]")
        st.write(f":red[*Overall returns for {sel_fund} are negative. If you are using entire fund as an investment reference"
                 f", we recommend going short in the fund*]")

with st.container(border=True):
    st.markdown("#### Investment Strategy for Individual Stocks")
    st.write("For individual stocks, we recommend the following strategies based on their returns:")

    new_df_2 = pd.DataFrame(columns = ['Ticker', 'Investment Decision'])
    for index, row in new_df.iterrows():
        if row['Returns'] > 0:
            new_df_2.loc[len(new_df_2)] = [row['Ticker'], '💲 Long']
        else:
            new_df_2.loc[len(new_df_2)] = [row['Ticker'], '❌ Short']


    new_df_2.sort_values(by='Investment Decision', ascending=False, inplace=True)
    st.dataframe(new_df_2, hide_index=True)