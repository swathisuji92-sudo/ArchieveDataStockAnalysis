import pandas as pd
import numpy as np
import sys
import os
import glob
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def daily_return_of_stock(sorted_ticker_wise_data):
    daily_return=[]
    prev_close_price = 0.0
    skipSymbolFirstFlag=True
    for rec in sorted_ticker_wise_data.itertuples(index=False):
        close_price=float(rec[1])
        if skipSymbolFirstFlag:
            skipSymbolFirstFlag=False
        else:
            daily_return.append((close_price-prev_close_price)/prev_close_price)
        prev_close_price=close_price
    return daily_return


if len(sys.argv) > 1:
        src_file_dir = sys.argv[1]
        print('src file dir::',src_file_dir)
else:
    sys.exit(5)
#src_file_dir='/Users/manikandan/Documents/Sujitha/stockAnalysis/csvData/'
csv_files = glob.glob(os.path.join(src_file_dir, "*.csv"))
csv_data=pd.DataFrame()
for f in csv_files:
    print(f'Processing File:: {f}')
    if csv_data.empty:
        csv_data=pd.read_csv(f)
    else:
        csv_data=pd.concat([csv_data,pd.read_csv(f)],axis=0)

print(csv_data.head(5))
unique_ticker=csv_data['Ticker'].unique()
st.title("!!! Welcome to the Stock Analysis Portal !!!")
analOption=st.selectbox("Select Analysis option category:",("Top 10 Volatile Stocks", "Cumulative Return for Top 5 Performing Stocks", 
             "Average Yearly Return by Sector", "Stock Price Correlation Heatmap", "Top 5 Gainers and Losers by Month"), placeholder="--Select the option for analysis--")

if analOption == "Top 10 Volatile Stocks":
    volatality_anal={}
    for i in unique_ticker:
            ticker_wise_data = csv_data[csv_data['Ticker']==i]
            sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
            daily_return=daily_return_of_stock(sorted_ticker_wise_data)
            std_dev=np.std(np.array(daily_return))
            volatality_anal[i]=std_dev

    volatality_anal_df=pd.DataFrame.from_dict(volatality_anal,orient='index',columns=['volatality'])
    volatality_anal_df=volatality_anal_df.sort_values(by=['volatality'],ascending=False,axis=0)
    st.bar_chart(volatality_anal_df.head(10),y="volatality",x_label="Ticker",y_label="Volatality")

elif analOption == "Cumulative Return for Top 5 Performing Stocks":
    cum_ret_anal={}
    ind_cum_ret={}
    for i in unique_ticker:
            ticker_wise_data = csv_data[csv_data['Ticker']==i]
            sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
            final_cum_return=0.0
            cum_ret=[]
            daily_return=0.0
            prev_close_price = 0.0
            skipSymbolFirstFlag=True
            for rec in sorted_ticker_wise_data.itertuples(index=False):
                close_price=float(rec[1])
                if skipSymbolFirstFlag:
                    skipSymbolFirstFlag=False
                else:
                    daily_return=((close_price-prev_close_price)/prev_close_price)
                final_cum_return+=daily_return
                cum_ret.append(final_cum_return)
                prev_close_price=close_price
            ind_cum_ret[i]=cum_ret
            cum_ret_anal[i]=final_cum_return

    cum_ret_anal_df=pd.DataFrame.from_dict(cum_ret_anal,orient='index',columns=['cumulative_return'])
    cum_ret_anal_df=cum_ret_anal_df.sort_values(by=['cumulative_return'],ascending=False,axis=0)
    print(cum_ret_anal_df.head(10))
    for i in cum_ret_anal_df.head(5).index:
        ind_cum_ret_df=pd.DataFrame({i:ind_cum_ret[i]})
        st.line_chart(ind_cum_ret_df,x_label=i,y_label="Cumulative Return")

elif analOption == "Average Yearly Return by Sector":

    sector_file_dir='/Users/manikandan/Documents/Sujitha/stockAnalysis/'
    sector_df=pd.read_csv('/Users/manikandan/Documents/Sujitha/stockAnalysis/Sector_data-Sheet1.csv')
    sector_df['Ticker']=sector_df.apply(lambda x : str(x['Symbol']).split(':')[1].strip(), axis=1)
    sector_df=sector_df.drop(columns=['COMPANY','Symbol'])
    sector_df.loc[sector_df['Ticker']=='ADANIGREEN','Ticker']='ADANIENT'
    sector_df.loc[sector_df['Ticker']=='AIRTEL','Ticker']='BHARTIARTL'
    sector_df.loc[sector_df['Ticker']=='TATACONSUMER','Ticker']='TATACONSUM'
    sector_df.loc[len(sector_df)]=['FMCG','BRITANNIA']
    avg_daily_ret={}
    for i in unique_ticker:
        ticker_wise_data = csv_data[csv_data['Ticker']==i]
        sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
        daily_return=daily_return_of_stock(sorted_ticker_wise_data)
        avg_daily_ret[i]=np.average(daily_return)
       
    avg_daily_ret_df=pd.DataFrame.from_dict(avg_daily_ret,orient='index',columns=['Average Yearly Return'])

    # Gather sector wise data and create dataset
    sector_vs_avg_return=pd.DataFrame(columns=['sector','average_yearly_return'])
    for sector in sector_df['sector'].unique():
        sector_wise_ticker=sector_df[sector_df['sector']==sector]['Ticker'].array
        sector_sum_avg_return=0.0
        for ticker in sector_wise_ticker:
            if avg_daily_ret.keys().__contains__(ticker):
                sector_sum_avg_return+=avg_daily_ret[ticker]
        sector_sum_avg_return=(sector_sum_avg_return/len(sector_wise_ticker))*100
        sector_vs_avg_return.loc[len(sector_vs_avg_return)]=[sector,sector_sum_avg_return]
    print(sector_vs_avg_return)

    st.bar_chart(sector_vs_avg_return, x='sector', y='average_yearly_return', x_label='Sector', y_label='Average Yearly Return (%)',width="stretch")

elif analOption=='Stock Price Correlation Heatmap':
    corr_data=csv_data[['Ticker','close','Date','Month','Year']]
    corr_data['calendar_date']=corr_data.apply(lambda x: '-'.join([str(x['Year']),str(x['Month']),str(x['Date'])]),axis=1)
    corr_data=corr_data.drop(columns=['Year','Date','Month'])
    print(corr_data.head(10))
    corr_df=corr_data.pivot(index='calendar_date', columns='Ticker', values='close')
    print(corr_df.head(5)) 
    corr_chart=corr_df.pct_change().corr()
    fig, ax = plt.subplots(figsize=(25, 25))
    sns.heatmap(corr_chart, annot=False, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
    st.pyplot(fig,width="stretch")

elif analOption=='Top 5 Gainers and Losers by Month':
    years=csv_data['Year'].unique()
    for year in years:
        current_year_data=csv_data[csv_data['Year']==year]
        for month in current_year_data['Month'].unique():
            ticker_vs_avg_monthly_ret=pd.DataFrame(columns=['Ticker','monthly_return','Month-Year'])
            for i in unique_ticker:
                curr_month_data = current_year_data[(current_year_data['Ticker']==i) & (current_year_data['Month']==month)].sort_values(by=['Date'],ascending=True)
                daily_return=daily_return_of_stock(curr_month_data)
                ticker_vs_avg_monthly_ret.loc[len(ticker_vs_avg_monthly_ret)]=[i,np.sum(daily_return),f'{month}-{year}']
                ticker_vs_avg_monthly_ret=ticker_vs_avg_monthly_ret.sort_values(by=['monthly_return'],ascending=False)
                filtered_df=ticker_vs_avg_monthly_ret.head(5)
                filtered_df=pd.concat([filtered_df,ticker_vs_avg_monthly_ret.tail(5)],axis=0)
            fig = px.bar(
                    filtered_df,
                    x="Ticker",
                    y="monthly_return",
                    color=filtered_df["monthly_return"] > 0, 
                    color_discrete_map={True: "green", False: "red"}, 
                    text_auto=True,
                    title=f'Montly Return for Calendar : {month}-{year}'
                )
            fig.update_layout(
                    yaxis={"tickformat": ".0%"},
                    xaxis_title="Ticker",
                    yaxis_title="Monthly Average (%)",
                    showlegend=False
                )
            st.plotly_chart(fig, width="stretch")












     