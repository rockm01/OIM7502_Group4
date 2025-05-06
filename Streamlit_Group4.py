import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import yfinance as yf
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
    st.image('Images/Stock Image.jpg')


    ##========== Display a filtered dataset with the latest date ==========##
    #Start Section
    st.title('ARK Funds Information')

    with st.container(border=True):
        sel_fund = st.selectbox('Choose Fund', fund_names, index=1)

    #Create Tabs to flip between pie chart and dataframe
    tab1, tab2, tab3 = st.tabs(['Pie Chart', 'Performance', 'Dataframe'])

    #Create Pie Charts
    pie_data = latest_data[latest_data['fund'] == sel_fund]
    fig = px.pie(
        pie_data,
        names='ticker',
        values='market value ($)',
        title='Current Fund Holding Profile'
    )
    tab1.plotly_chart(fig)

    #Create Performance Trend Line Chart
    fund_trend_df = db_df[db_df['fund']==sel_fund]
    fund_trend_df = fund_trend_df.groupby('date')['market value ($)'].agg('sum')
    tab2.line_chart(fund_trend_df)
    #Create Dataframe
    tab3.dataframe(
        latest_data[latest_data['fund'] == sel_fund][
            ['fund', 'company', 'ticker', 'shares', 'market value ($)', 'weight (%)'
             ]
        ],
        width=800, hide_index=True
    )


    st.divider()


    with st.container(border=True):
        sel_fund = st.selectbox('Select a fund', fund_names, index=1)

        left, right = st.columns(2)
        with left:
            num = st.text_input('Number of Periods', value=1)
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
    
    graph_df = (mystocks.data.unstack()).reset_index()
    graph_df = graph_df[graph_df['Price'] == 'Close']
    graph_df = graph_df.rename(columns={0: "Close Price"})


    # Create a line graph
    tick_names = graph_df['Ticker'].unique().tolist()
    fig, ax = plt.subplots(nrows=len(tick_names), ncols=1, sharex=True, figsize=(10,20))
    if len(tick_names)==1:
        x = graph_df[graph_df['Ticker']==tick_names[0]]['Date']
        y = graph_df[graph_df['Ticker']==tick_names[0]]['Close Price']
        ax.plot(x, y)
        ax.set_title(tick_names[0])
        ax.set_ylabel("Share Price ($)")
        fig.autofmt_xdate()
        tab1.pyplot(fig)
    else:    
        for ticks, ax in zip(tick_names, ax):
            x = graph_df[graph_df['Ticker']==ticks]['Date']
            y = graph_df[graph_df['Ticker']==ticks]['Close Price']
            ax.plot(x, y)
            ax.set_title(ticks)
            ax.set_ylabel("Share Price ($)")
        fig.autofmt_xdate()
        tab1.pyplot(fig)


    tab2.dataframe(new_df, use_container_width=True, hide_index=True)
    tab3.dataframe(graph_df, use_container_width=True, hide_index=True)



##========== Investment Strategy Page ==========##
if page == "Investment Strategy":
    st.image('Images/Invest Image.jpg')
    st.markdown("## Investment Strategy:")
    st.markdown('##### Choose Fund and Date Range for Investment Decision')

    # Start Section
    with st.container(border=True):
        fund2 = st.selectbox('Select Fund', fund_names, index=1)

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
    tab1, tab2 = st.tabs(['Bar Chart', 'Fund Dataframe'])
    a_chart1 = alt.Chart(grouped_df).mark_bar(color='steelblue').encode(
        x=alt.X("ticker:O").axis(labelAngle=90),
        y=alt.Y("change:Q")
    ).properties(title="Bar Chart of Fund Holdings Change")
    tab1.altair_chart(a_chart1)
    tab2.dataframe(grouped_df, width=1600, hide_index=True)
   

    st.divider()


    st.markdown('#### Investment Recommendation')
    st.write("Based on the analysis of the selected fund's top holdings, we recommend focusing on the following strategies:")


    #Calculate Fund's Return and volatility:
    sliced_df2 = db_df[(db_df['fund'] == fund2) & ((db_df['date'] == start_date) | (db_df['date'] == end_date))]
    grouped_df2 = sliced_df2.groupby(['fund', 'ticker', 'date'])['market value ($)'].sum().unstack().fillna(0)
    grouped_df2.reset_index(inplace=True)
    grouped_df2['change'] = grouped_df2[end_date] - grouped_df2[start_date]
    fund_change = grouped_df2['change'].sum()
    fund_pct_ret = (fund_change / (grouped_df2[start_date].sum())) * 100


    #Identify stocks from selected fund for use in pulling data
    stocks = db_df[db_df['fund'] == fund2]['ticker'].unique()
    stocks = stocks.tolist()
    stocks = [(lambda x: x.replace(" UQ", ""))(item) for item in stocks]

    #Define period for pulling volatility
    prd = str((end_date - start_date).days) + 'd'


    #Pull data for selected fund
    def main():
        mystocks = Stock(stocks, period=prd)
        new_df2 = mystocks.calc_returns()
        return new_df2

    if __name__ == "__main__":
        new_df2 = main()
    
    
    fund_volatility = (new_df2['Volatility'].mean()) 


    #S&P Returns and volatility for comparison:
    def main():
        mystocks = Stock('^GSPC', period=prd)
        sp_df = mystocks.calc_returns()
        return sp_df

    if __name__ == "__main__":
        sp_df = main()


    sp_pct_ret = sp_df.iloc[0]['Percent Change (%)']
    sp_volatility = sp_df.iloc[0]['Volatility']
    

    #Display Investment Recommendation based on performance
    with st.container(border=True):
        st.markdown("#### Investment Strategy for Aggregated Fund")

        left_col, right_col = st.columns(2)
        with left_col:
            st.write(f'S&P 500 Cumulative Return (%): {sp_pct_ret:0.3f}%')

            if fund_pct_ret > sp_pct_ret:
                st.write(''':chart_with_upwards_trend:''', 
                         f"{fund2} Cumulative Return (%): :green[${fund_pct_ret:.3f}%]")
                
                inv_string = 'overperformed'
                inv_string2 = ""

            else:
                st.write(''':chart_with_downwards_trend:''', 
                         f"{fund2} Cumulative Return (%): :red[{fund_pct_ret:.3f}%]")
                
                inv_string = 'underperformed'
                inv_string2 = "don't"

        with right_col:
            st.write(f'S&P 500 Volatility: {sp_volatility:0.2f}')
            if fund_volatility < sp_volatility:
                st.write('✅', f"{fund2} Volatility: :green[{fund_volatility:.2f}]")
                inv_string3 = "lower"
            else:
                st.write('⚠️', f"{fund2} Volatility: :red[{fund_volatility:.2f}]")
                inv_string3 = "higher"
        
        
        st.write(f"{fund2} {inv_string} relative to the S&P 500. Using the entire fund as a reference,",
                 f"we {inv_string2} recommend investing in {fund2}")
        st.markdown(f"*Note that {fund2} has a {inv_string3} risk profile than the S&P 500, which could affect your decision to invest*")



    #Investment Decision for Individual Stocks
    with st.container(border=True):
        st.markdown("#### Investment Strategy for Individual Stocks")
        st.write("For individual stocks, we recommend the following strategies based on their performance:")
        risk_opts = ['✅ Low', '⚠️ Medium', "‼️HIGH‼️"]
        pill_var = st.pills('Filter by Risk', risk_opts, selection_mode='multi', default=risk_opts)

        new_df3 = pd.DataFrame(columns = ['Ticker', 'Investment Decision', 'Risk Profile'])
        for index, row in new_df2.iterrows():
            if row['Percent Change (%)'] > sp_pct_ret:
                inv_dec = '💲 Long'
            else:
                inv_dec = '❌ Short'
            
            if row['Volatility'] <= (sp_volatility):
                risk = risk_opts[0]
            elif row['Volatility'] <= (sp_volatility * 3.5):
                risk = risk_opts[1]
            else:
                risk = risk_opts[2]
            
            new_df3.loc[len(new_df3)] = [row['Ticker'], inv_dec, risk]

        if len(pill_var) > 0:
            new_df3_filt = new_df3[new_df3['Risk Profile'].isin(pill_var)]
            new_df3_filt.sort_values(by='Investment Decision', ascending=False, inplace=True)
            st.dataframe(new_df3_filt, hide_index=True)